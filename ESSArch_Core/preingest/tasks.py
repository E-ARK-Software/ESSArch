"""
    ESSArch is an open source archiving and digital preservation system

    ESSArch
    Copyright (C) 2005-2019 ES Solutions AB

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program. If not, see <https://www.gnu.org/licenses/>.

    Contact information:
    Web - http://www.essolutions.se
    Email - essarch@essolutions.se
"""

import os
import shutil

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction

# noinspection PyUnresolvedReferences
from ESSArch_Core import tasks  # noqa
from ESSArch_Core.configuration.models import Path
from ESSArch_Core.ip.models import Agent, InformationPackage
from ESSArch_Core.storage.copy import copy_file
from ESSArch_Core.WorkflowEngine.dbtask import DBTask

User = get_user_model()


class ReceiveIP(DBTask):
    event_type = 20100

    @transaction.atomic
    def run(self):
        ip = InformationPackage.objects.get(pk=self.ip)
        sa = ip.submission_agreement
        preingest_path = Path.objects.get(entity="preingest").value
        dst_dir = os.path.join(preingest_path, ip.object_identifier_value)
        shutil.copytree(ip.object_path, dst_dir)

        if sa.archivist_organization:
            existing_agents_with_notes = Agent.objects.all().with_notes([])
            ao_agent, _ = Agent.objects.get_or_create(
                role='ARCHIVIST', type='ORGANIZATION',
                name=sa.archivist_organization, pk__in=existing_agents_with_notes
            )
            ip.agents.add(ao_agent)

        submit_description_data = ip.get_profile_data('submit_description')
        ip.label = ip.object_identifier_value
        ip.entry_date = ip.create_date
        ip.object_path = dst_dir
        ip.start_date = submit_description_data.get('start_date')
        ip.end_date = submit_description_data.get('end_date')
        ip.save()

    def event_outcome_success(self, result):
        return "Received IP"


class TransferSIP(DBTask):
    event_type = 20600

    def run(self):
        ip = InformationPackage.objects.get(pk=self.ip)
        src = ip.object_path
        srcdir, srcfile = os.path.split(src)
        dst = Path.objects.get(entity="gate_reception").value

        try:
            remote = ip.get_profile_data('transfer_project').get(
                'preservation_organization_receiver_url_epp'
            )
        except AttributeError:
            remote = None

        session = None

        if remote:
            try:
                dst, remote_user, remote_pass = remote.split(',')

                session = requests.Session()
                session.verify = settings.REQUESTS_VERIFY
                session.auth = (remote_user, remote_pass)
            except ValueError:
                remote = None
        else:
            dst = os.path.join(dst, srcfile)

        block_size = 8 * 1000000  # 8MB

        copy_file(src, dst, requests_session=session, block_size=block_size)

        self.set_progress(50, total=100)

        objid = ip.object_identifier_value
        src = ip.get_events_file_path()
        if os.path.isfile(src):
            if not remote:
                xml_dst = os.path.join(os.path.dirname(dst), "%s_ipevents.xml" % objid)
            else:
                xml_dst = dst
            copy_file(src, xml_dst, requests_session=session, block_size=block_size)

        self.set_progress(75, total=100)

        src = os.path.join(srcdir, "%s.xml" % objid)
        if not remote:
            xml_dst = os.path.join(dst, "%s.xml" % objid)
        copy_file(src, xml_dst, requests_session=session, block_size=block_size)

        self.set_progress(100, total=100)

        return dst

    def undo(self):
        objectpath = InformationPackage.objects.values_list('object_path', flat=True).get(pk=self.ip)

        ipdir, ipfile = os.path.split(objectpath)
        gate_reception = Path.objects.get(entity="gate_reception").value

        objid = InformationPackage.objects.values_list(
            'object_identifier_value', flat=True
        ).get(pk=self.ip)

        os.remove(os.path.join(gate_reception, ipfile))
        os.remove(os.path.join(gate_reception, "%s.xml" % objid))

    def event_outcome_success(self, result, *args, **kwargs):
        return "Transferred IP"
