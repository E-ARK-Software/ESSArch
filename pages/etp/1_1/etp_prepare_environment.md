---
title: Prepare Environment
tags: [getting_started, troubleshooting]
keywords:
summary: "Prepare Environment"
sidebar: etp_sidebar_1_1
permalink: etp_prepare_environment_1_1.html
folder: etp_1_1
---

## Customize user environment for arch user

Add the following rows to /home/arch/.bash_profile after "ESSArch Core" section:

    ### ETP start
    ##
    export ETP=/ESSArch/pd/python/lib/python2.7/site-packages/ESSArch_TP
    export PYTHONPATH=$ETP:$EC_PYTHONPATH
    alias env_etp='export PYTHONPATH=$ETP:$EC_PYTHONPATH;cd $ETP'
    ##
    ### ETP end

**Note:** If you install multiple ESSArch products such as ETP, ETA or the EPP on the same server, you must adapt PYTHONPATH so that only one product is used at a time. As an alternative, you can run the alias env_etp, env_eta or env_epp that configure PYTHONPATH for each product before you is performing operations.

[<img align="right" src="images/n.png">](etp_install_1_1.html)
{% include links.html %}
