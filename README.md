<!--
SPDX-FileCopyrightText: Copyright 2004-present Facebook. All Rights Reserved.
SPDX-FileCopyrightText: 2019-present Open Networking Foundation <info@opennetworking.org>

SPDX-License-Identifier: Apache-2.0
-->

# OSC near-RT RIC xApp development template

Adapt this development template to create your xApp on the OSC RIC.


## Prerequisite

Refer to this tutorial (https://github.com/5GSEC/OAI-5G-Docker/blob/master/O-RAN%20SC%20RIC%20Deployment%20Guide.md) to set up the OSC near-RT RIC environment.


## Build the xApp

First onboard the xApp:

```
cd init
sudo -E dms_cli onboard --config_file_path=config-file.json --shcema_file_path=schema.json
```

Build the xApp docker image:

```
./build.sh
```

After a successful build, the xApp will be compiled as a standalone Docker container. You can confirm with:

```
$ docker images
```


## Deploy the xApp

```
./deploy.sh
```


## Undeploy the xApp

```
./undeploy.sh
```
``

