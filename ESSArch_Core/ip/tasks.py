import logging
import os
import shutil
import tarfile
from urllib.parse import urljoin

import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from django.utils.translation import ugettext as _

from ESSArch_Core.auth.models import Notification
from ESSArch_Core.configuration.models import Path
from ESSArch_Core.essxml.Generator.xmlGenerator import XMLGenerator
from ESSArch_Core.fixity.receipt import get_backend as get_receipt_backend
from ESSArch_Core.fixity.transformation import get_backend as get_transformer
from ESSArch_Core.ip.models import Agent, EventIP, InformationPackage
from ESSArch_Core.ip.utils import (
    download_schemas,
    generate_aic_mets,
    generate_content_mets,
    generate_events_xml,
    generate_package_mets,
    generate_premis,
    get_cached_objid,
    parse_submit_description_from_ip,
)
from ESSArch_Core.profiles.utils import fill_specification_data
from ESSArch_Core.storage.copy import copy_file
from ESSArch_Core.storage.models import StorageMethod, StorageTarget
from ESSArch_Core.util import (
    get_premis_ip_object_element_spec,
    normalize_path,
    zip_directory,
)
from ESSArch_Core.WorkflowEngine.dbtask import DBTask
from ESSArch_Core.WorkflowEngine.models import ProcessTask

User = get_user_model()


class ReceiveSIP(DBTask):
    event_type = 20100

    @transaction.atomic
    def run(self):
        ip = InformationPackage.objects.get(pk=self.ip)
        sa = ip.submission_agreement
        prepare_path = Path.objects.get(entity="path_preingest_prepare").value
        dst_dir = os.path.join(prepare_path, ip.object_identifier_value)
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

    def event_outcome_success(self, result, *args, **kwargs):
        return "Received IP"


class SubmitSIP(DBTask):
    event_type = 10500

    def run(self):
        ip = InformationPackage.objects.get(pk=self.ip)

        srcdir = Path.objects.get(entity="path_preingest_reception").value
        reception = Path.objects.get(entity="path_ingest_reception").value
        container_format = ip.get_container_format()
        src = os.path.join(srcdir, ip.object_identifier_value + ".%s" % container_format)

        try:
            remote = ip.get_profile('transfer_project').specification_data.get(
                'preservation_organization_receiver_url'
            )
        except AttributeError:
            remote = None

        session = None

        if remote:
            try:
                dst, remote_user, remote_pass = remote.split(',')
                dst = urljoin(dst, 'api/ip-reception/upload/')

                session = requests.Session()
                session.verify = settings.REQUESTS_VERIFY
                session.auth = (remote_user, remote_pass)
            except ValueError:
                remote = None
        else:
            dst = os.path.join(reception, ip.object_identifier_value + ".%s" % container_format)
        block_size = 8 * 1000000  # 8MB
        copy_file(src, dst, requests_session=session, block_size=block_size)

        src = os.path.join(srcdir, ip.object_identifier_value + ".xml")
        if not remote:
            dst = os.path.join(reception, ip.object_identifier_value + ".xml")
        copy_file(src, dst, requests_session=session, block_size=block_size)

        self.set_progress(100, total=100)

    def undo(self):
        ip = InformationPackage.objects.get(pk=self.ip)

        reception = Path.objects.get(entity="path_ingest_reception").value
        container_format = ip.get_container_format()

        tar = os.path.join(reception, ip.object_identifier_value + ".%s" % container_format)
        xml = os.path.join(reception, ip.object_identifier_value + ".xml")

        os.remove(tar)
        os.remove(xml)

    def event_outcome_success(self, result, *args, **kwargs):
        return "Submitted %s" % get_cached_objid(self.ip)


class GenerateContentMets(DBTask):
    event_type = 50600

    def run(self):
        generate_content_mets(self.get_information_package())

    def event_outcome_success(self, result, *args, **kwargs):
        ip = self.get_information_package()
        return 'Generated {xml}'.format(xml=ip.content_mets_path)


class GeneratePackageMets(DBTask):
    event_type = 50600

    def run(self, package_path=None, xml_path=None):
        ip = self.get_information_package()
        package_path = package_path if package_path is not None else ip.object_path
        xml_path = xml_path if xml_path is not None else os.path.splitext(package_path)[0] + '.xml'

        generate_package_mets(ip, package_path, xml_path)
        return xml_path

    def event_outcome_success(self, result, *args, **kwargs):
        return 'Generated {xml}'.format(xml=result)


class GenerateAICMets(DBTask):
    def run(self, xml_path):
        ip = self.get_information_package()
        generate_aic_mets(ip, xml_path)
        return xml_path

    def event_outcome_success(self, result, *args, **kwargs):
        return 'Generated {xml}'.format(xml=result)


class GeneratePremis(DBTask):
    event_type = 50600

    def run(self):
        generate_premis(self.get_information_package())

    def event_outcome_success(self, result, *args, **kwargs):
        ip = self.get_information_package()
        return 'Generated {xml}'.format(xml=ip.get_premis_file_path())


class GenerateEventsXML(DBTask):
    event_type = 50600

    def run(self):
        generate_events_xml(self.get_information_package())

    def event_outcome_success(self, result, *args, **kwargs):
        ip = self.get_information_package()
        return 'Generated {xml}'.format(xml=ip.get_events_file_path())


class DownloadSchemas(DBTask):
    logger = logging.getLogger('essarch.core.ip.tasks.DownloadSchemas')

    def run(self, verify=True):
        download_schemas(self.get_information_package(), self.logger, verify)


class AddPremisIPObjectElementToEventsFile(DBTask):
    def run(self):
        ip = self.get_information_package()
        info = {
            'FIDType': "UUID",
            'FID': ip.object_identifier_value,
            'FFormatName': ip.get_container_format().upper(),
            'FLocationType': 'URI',
            'FName': ip.object_path,
        }
        spec = get_premis_ip_object_element_spec()
        info = fill_specification_data(info, ip=ip)
        xmlfile = os.path.join(ip.object_path, ip.get_events_file_path())

        generator = XMLGenerator(filepath=xmlfile)
        target = generator.find_element('premis')
        generator.insert_from_specification(target, spec, data=info, index=0)
        generator.write(xmlfile)


class CreatePhysicalModel(DBTask):
    event_type = 10300

    def run(self, structure=None, root=""):
        """
        Creates the IP physical model based on a logical model.

        Args:
            structure: A dict specifying the logical model.
            root: The root directory to be used
        """

        ip = self.get_information_package()
        ip.create_physical_model(structure, root)

        self.set_progress(1, total=1)

    def event_outcome_success(self, result, *args, **kwargs):
        return "Created physical model for %s" % self.ip_objid


class CreateContainer(DBTask):
    def run(self, src, dst):
        ip = self.get_information_package()
        container_format = ip.get_container_format().lower()
        tpp = ip.get_profile_rel('transfer_project').profile
        compress = tpp.specification_data.get('container_format_compression', False)

        dst = normalize_path(dst)

        if container_format == 'zip':
            self.event_type = 50410
            zip_directory(dirname=src, zipname=dst, compress=compress)
        else:
            self.event_type = 50400
            compression = ':gz' if compress else ''
            base_dir = os.path.basename(os.path.normpath(src))
            with tarfile.open(dst, 'w%s' % compression) as new_tar:
                new_tar.add(src, base_dir)

        return dst


class ParseSubmitDescription(DBTask):
    @transaction.atomic
    def run(self):
        parse_submit_description_from_ip(self.get_information_package())

    def event_outcome_success(self, result, *args, **kwargs):
        ip = self.get_information_package()
        return "Parsed submit description at {}".format(ip.package_mets_path)


class ParseEvents(DBTask):
    event_type = 50630

    def get_path(self, ip):
        return ip.get_events_file_path(from_container=True)

    @transaction.atomic
    def run(self):
        ip = self.get_information_package()
        xmlfile = ip.open_file(self.get_path(ip), 'rb')
        events = EventIP.objects.from_premis_file(xmlfile, save=False)
        EventIP.objects.bulk_create(events, 100)

    def event_outcome_success(self, result, *args, **kwargs):
        ip = self.get_information_package()
        return "Parsed events from %s" % self.get_path(ip)


class Transform(DBTask):
    def run(self, backend, path=None):
        ip = self.get_information_package()
        user = User.objects.filter(pk=self.responsible).first()
        backend = get_transformer(backend, ip, user)
        if path is None and ip is not None:
            path = ip.object_path
        backend.transform(path)


class PreserveInformationPackage(DBTask):
    def run(self, storage_method_pk):
        ip = self.get_information_package()
        policy = ip.policy

        if policy is None:
            raise ValueError('{} has no policy'.format(ip))

        storage_method = StorageMethod.objects.get(pk=storage_method_pk)
        policy_methods = policy.storage_methods.all()

        if storage_method not in policy_methods and storage_method != policy.cache_storage:
            raise ValueError('{} not part of {}'.format(storage_method, policy))

        try:
            storage_target = storage_method.enabled_target
        except StorageTarget.DoesNotExist:
            raise ValueError('No writeable target available for {}'.format(storage_method))

        if storage_method.containers or storage_target.remote_server:
            src = [
                ip.get_temp_container_path(),
                ip.get_temp_container_xml_path(),
                ip.get_temp_container_aic_xml_path(),
            ]
        else:
            src = [ip.object_path]

        return ip.preserve(src, storage_target, storage_method.containers, self.get_processtask())


class WriteInformationPackageToSearchIndex(DBTask):
    def run(self):
        ip = self.get_information_package()
        ip.write_to_search_index()


class CreateReceipt(DBTask):
    def run(self, task_id, backend, template, destination, outcome, short_message, message, date=None):
        ip = self.get_information_package()
        template, destination, outcome, short_message, message, date = self.parse_params(
            template, destination, outcome, short_message, message, date
        )
        if date is None:
            date = timezone.now()

        backend = get_receipt_backend(backend)
        if task_id is None:
            task = self.get_processtask()
        else:
            task = ProcessTask.objects.get(pk=task_id)
        backend.create(template, destination, outcome, short_message, message, date, ip=ip, task=task)


class MarkArchived(DBTask):
    def run(self):
        ip = self.get_information_package()
        ip.archived = True
        ip.state = 'Preserved'
        ip.save()


class DeleteInformationPackage(DBTask):
    def run(self, from_db=False, delete_files=True):
        ip = self.get_information_package()

        old_state = ip.state
        ip.state = 'Deleting'
        ip.save()
        try:
            ip.delete_workareas()
            if delete_files:
                ip.delete_files()
        except BaseException:
            ip.state = old_state
            ip.save()
            raise

        self.set_progress(99, 100)

        if from_db:
            ip.delete()
        else:
            ip.state = 'deleted'
            ip.save()

        Notification.objects.create(message=_('%(ip)s has been deleted') % {'ip': ip.object_identifier_value},
                                    level=logging.INFO, user_id=self.responsible, refresh=True)
