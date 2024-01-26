<!--
SPDX-FileCopyrightText: Copyright 2004-present Facebook. All Rights Reserved.
SPDX-FileCopyrightText: 2019-present Open Networking Foundation <info@opennetworking.org>

SPDX-License-Identifier: Apache-2.0
-->

# MobiFlow-Auditor-xApp

MobiFlow Auditor is an O-RAN compliant xApp aiming to support ***fine-grained and security-aware statistics monitoring over the RAN data plane***, which is not solved by the default O-RAN standard and service models. We abstract such telemetry streams as **MobiFlow**, a novel security audit trail for holding mobile devices accountable during the link and session setup protocols as they interact with the base station, and interval statistics generated for tracking large-scale patterns of abuse against the base station.

MobiFlow Auditor can drive various analyses. For example, it can drive expert system analysis with MobiExpert (https://github.com/5GSEC/mobi-expert-xapp). MobiExpert xApp allows network operators to program stateful production-based IDS rules for detecting a wide range of cellular L3 attacks. It features the Production-Based Expert System Toolset ([P-BEST](https://ieeexplore.ieee.org/document/766911)) language. MobiFlow Auditor can also drive AI / ML-based analytics. 

To learn more about the format and structure of MobiFlow, please refer to our papers:

- [A Fine-Grained Telemetry Stream for Security Services in 5G Open Radio Access Networks](https://dl.acm.org/doi/abs/10.1145/3565474.3569070) (EmergingWireless'22)
- [5G-Spector: An O-RAN Compliant Layer-3 Cellular Attack Detection Service](https://web.cse.ohio-state.edu/~wen.423/papers/5G-Spector-NDSS24.pdf) (NDSS'24)

The current implementation of MobiFlow Auditor is dedicated to the [ONOS RIC](https://docs.onosproject.org/v0.6.0/onos-cli/docs/cli/onos_ric/) on [SD-RAN](https://docs.sd-ran.org/master/index.html) and OpenAirInterface5G (https://gitlab.eurecom.fr/oai/openairinterface5g/).
It is developed based on the [ONOS RIC's python SDK](https://github.com/onosproject/onos-ric-sdk-py) and guidance from the exemplar [ONOS RAN Intelligent Controller xApps](https://github.com/onosproject/onos-ric-python-apps/)  authored in Python programming language.


## Prerequisite

MobiFlow-Auditor is built as a Docker container. Refer to the official tutorial (https://docs.docker.com/engine/install/) to install and set up the Docker environment.

Create a local docker registry to host docker images: 

```
sudo docker run -d -p 5000:5000 --restart=always --name registry registry:2
```

## Build the MobiFlow-Auditor xApp

```
./build.sh
```

After a successful build, the xApp will be compiled as a standalone Docker container.

```
$ docker images
localhost:5000/mobiflow-auditor           latest    722a04c343b8   9 days ago     255MB
```


## Install the MobiFlow-Auditor xApp

We have provided a default helm chart for deploying MobiFlow-Auditor on the ONOS RIC via [Kubernetes](https://kubernetes.io/) and [Helm](https://helm.sh/).

```
./install_xapp.sh
```

## Uninstall MobiFlow-Auditor xApp

Undeploy the MobiFlow-Auditor xApp from Kubernetes

```
./uninstall_xapp.sh
```


## Publication

```
@inproceedings{wen2022fine,
  title={A fine-grained telemetry stream for security services in 5g open radio access networks},
  author={Wen, Haohuang and Porras, Phillip and Yegneswaran, Vinod and Lin, Zhiqiang},
  booktitle={Proceedings of the 1st International Workshop on Emerging Topics in Wireless},
  pages={18--23},
  year={2022}
}
```

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
