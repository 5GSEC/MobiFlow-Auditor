<!--
SPDX-FileCopyrightText: Copyright 2004-present Facebook. All Rights Reserved.
SPDX-FileCopyrightText: 2019-present Open Networking Foundation <info@opennetworking.org>

SPDX-License-Identifier: Apache-2.0
-->

# MobieXpert-xApp

MobieXpert xApp is the first L3 cellular attack detection xApp. 
MobieXpert’s design is based on the Production-Based Expert System Toolset ([P-BEST](https://ieeexplore.ieee.org/document/766911)) language, 
which has been widely used for decades in stateful intrusion detection. 
With MobieXpert, network operators can program stateful production-based IDS rules for detecting a wide range of cellular L3 attacks.

MobieXpert is an essential part of the 5G-Spector artifact. To learn more about 5G-Spector, please refer to our 
[paper](https://web.cse.ohio-state.edu/~wen.423/papers/5G-Spector-NDSS24.pdf) in NDSS'24
and the [5G-Spector](https://github.com/5GSEC/5G-Spector) git repository.

MobieXpert is dedicated for the [ONOS RIC](https://docs.onosproject.org/v0.6.0/onos-cli/docs/cli/onos_ric/) on [SD-RAN](https://docs.sd-ran.org/master/index.html).
It is developed based on the [ONOS RIC's python SDK](https://github.com/onosproject/onos-ric-sdk-py) and guidance from the exemplar [ONOS RAN Intelligent Controller xApps](https://github.com/onosproject/onos-ric-python-apps/)  authored in Python programming language.


## Prerequisite

MobieXpert is built as a Docker container. Refer to the official tutorial (https://docs.docker.com/engine/install/) to install and set up the Docker environment.

Create a local docker registry to host docker images: 

```
sudo docker run -d -p 5000:5000 --restart=always --name registry registry:2
```

## TODO

Decide how P-BEST source code is released


## Build the MobieXpert xApp

```
./build.sh
```

After a successful build, the xApp will be compiled as a standalone Docker container.

```
$ docker images
localhost:5000/mobiflow-auditor           latest    722a04c343b8   9 days ago     255MB
```




## Install the MobieXpert xApp

We have provided a default helm chart for deploying MobieXpert on the ONOS RIC via [Kubernetes](https://kubernetes.io/).

```
./install_secsm-xapp.sh
```

## Uninstall MobieXpert xApp

Undeploy the MobieXpert xApp from Kubernetes

```
./uninstall_secsm-xapp.sh
```


## Publication

```
@inproceedings{5G-Spector:NDSS24,
  title     = {5G-Spector: An O-RAN Compliant Layer-3 Cellular Attack Detection Service},
  author    = {Wen, Haohuang and Porras, Phillip and Yegneswaran, Vinod and Gehani, Ashish and Lin, Zhiqiang},
  booktitle = {Proceedings of the 31st Annual Network and Distributed System Security Symposium (NDSS'24)},
  address   = {San Diego, CA},
  month     = {February},
  year      = 2024
}
```
