<!--
SPDX-FileCopyrightText: Copyright 2004-present Facebook. All Rights Reserved.
SPDX-FileCopyrightText: 2019-present Open Networking Foundation <info@opennetworking.org>

SPDX-License-Identifier: Apache-2.0
-->

# MobiFlow-Auditor-xApp

MobiFlow Auditor is an O-RAN compliant xApp aiming to support ***fine-grained and security-aware statistics monitoring over the RAN data plane***, which is not solved by the default O-RAN standard and service models. We abstract such telemetry streams as **MobiFlow**, a novel security audit trail for holding mobile devices accountable during the link and session setup protocols as they interact with the base station, and interval statistics generated for tracking large-scale patterns of abuse against the base station.

MobiFlow Auditor can drive various analyses. For example, it can drive expert system analysis with [MobiExpert](https://github.com/5GSEC/MobieXpert). MobiExpert xApp allows network operators to program stateful production-based IDS rules for detecting a wide range of cellular L3 attacks. It features the Production-Based Expert System Toolset ([P-BEST](https://ieeexplore.ieee.org/document/766911)) language. MobiFlow Auditor can also drive AI / ML-based analytics, such as [MobiWatch](https://github.com/5GSEC/MobiWatch) that uses unsupervised deep learning to detect layer-3 anomalies from 5G network traffic.

To learn more about the format and structure of MobiFlow, please refer to our papers:

- [A Fine-Grained Telemetry Stream for Security Services in 5G Open Radio Access Networks](https://dl.acm.org/doi/abs/10.1145/3565474.3569070) (EmergingWireless'22)
- [5G-Spector: An O-RAN Compliant Layer-3 Cellular Attack Detection Service](https://web.cse.ohio-state.edu/~wen.423/papers/5G-Spector-NDSS24.pdf) (NDSS'24)

MobiFlow Auditor's current implementation is dedicated for the [OSC RIC](https://wiki.o-ran-sc.org/display/ORAN). It is developed based on the [OSC RIC's python SDK](https://github.com/o-ran-sc/ric-plt-xapp-frame-py). Our running example below shows how to setup a 5G network based on the [OpenAirInterface5G](https://gitlab.eurecom.fr/oai/openairinterface5g/) project.


We also have an old version implemented for the [ONOS RIC](https://docs.onosproject.org/v0.6.0/onos-cli/docs/cli/onos_ric/) on [SD-RAN](https://docs.sd-ran.org/master/index.html). It was used as part of the [5G-Spector](https://github.com/5GSEC/5G-Spector) but not recommended any more since the ONOS RIC xApp python SDK is no longer being maintained.



## Prerequisite

MobiFlow-Auditor is built from source as a local Docker container. Refer to the official tutorial (https://docs.docker.com/engine/install/) to install and set up the Docker environment.

Create a local docker registry to host docker images: 

```
sudo docker run -d -p 5000:5000 --restart=always --name registry registry:2
```


## MobiFlow Structure

The current MobiFlow message definition is defined in [mobiflow.py](./src/mobiflow/mobiflow.py#L60). It mainly collects (1) the fine-grained layer-3 (RRC and NAS) state transition information of UEs at the message level; (2) the aggregated flow-based statistics from the base stations. The MobiFlow telemetry report process is based on the E2SM-KPM (v2.0) service model (SM). 

MobiFlow Auditor xApp requires O-RAN compliant RAN nodes to collect and report corresponding data. We have augmented the OpenAirInterface project with MobiFlow telemetry support at [https://github.com/onehouwong/OAI-5G](https://github.com/5GSEC/OAI-5G) branch `v2.1.0.secsm.osc`.


## Build the MobiFlow-Auditor xApp

```
./build.sh
```

After a successful build, the xApp will be compiled as a standalone Docker container.

```
$ docker images
REPOSITORY                         TAG       IMAGE ID       CREATED          SIZE
localhost:5000/mobiflow-auditor    0.0.1     c6312eb0d32e   2 minutes ago    237M
```


## Install / Uninstall the MobiFlow-Auditor xApp

First, onboard the xApp. You need to set up the proper environment with the `dms_cli` tool. Follow the instructions [here](https://github.com/5GSEC/5G-Spector/wiki/O%E2%80%90RAN-SC-RIC-Deployment-Guide) to install the tool. 

Then execute the following to onboard the xApp:

```
cd init
sudo -E dms_cli onboard --config_file_path=config-file.json --shcema_file_path=schema.json
```

Then, simply run the script to deploy the xApp under the `ricxapp` K8S namespace in the nRT-RIC.

```
cd ..
./deploy.sh
```

Make sure the xApp is up and running:

```
$ kubectl get pods -n ricxapp
NAME                                READY   STATUS    RESTARTS   AGE
mobiflow-auditor-68d598d7fb-vhlqw   1/1     Running   0          4m10s
...
```

If you wish to undeploy the MobiFlow-Auditor xApp from Kubernetes, run:

```
./undeploy.sh
```

## Running Example

The below running example shows how to use the MobiFlow Auditor xApp to capture security telemetry from a live 5G network and stores the telemetry into the SDL database.

Before running, make sure the OSC nRT-RIC is deployed by following this [tutorial](https://github.com/5GSEC/5G-Spector/wiki/O%E2%80%90RAN-SC-RIC-Deployment-Guide#deploy-the-osc-near-rt-ric).

Next, deploy the OAI gNB that connects to the nRT-RIC through the E2 interface. You can refer to our [tutorial](https://github.com/5GSEC/5G-Spector/wiki/O%E2%80%90RAN-SC-RIC-Deployment-Guide#connect-oai-gnb-to-osc-ric) to deploy the OAI gNB which is extended with the E2 agent we have implemented. Ensure the gNB is up and connected to the RIC.


Run the MobiFlow Auditor xApp (assuming the image has been built):

```
./deploy.sh
```

Finally, run the OAI nrUE (or a commercial UE) to attach to the gNB and generate 5G traffic. We have provided instructions on how to run the OAI UE at this [link](https://github.com/5GSEC/5G-Spector/wiki/O%E2%80%90RAN-SC-RIC-Deployment-Guide#run-oai-ue).


After the gNB and UE is running. You can check the xApp log by running:

```
./log.sh
```


By running the MobiFlow Auditor on the RIC along with an OAI gNB and nrUE, MobiFlow Auditor will generate and store MobiFlow telemetry. You can check the run-time logs with:

```
{"ts": 1729716349154, "crit": "INFO", "id": "ricxappframe.xapp_frame", "mdc": {}, "msg": "[MobiFlow] Storing MobiFlow record to SDL UE;0;1729716349154.052;v2.0;SECSM;0;60786;1450744508;0;0;0;0;0;RRCSetupRequest;0;0;0;0;0;0;0;0"}
{"ts": 1729716349155, "crit": "INFO", "id": "ricxappframe.xapp_frame", "mdc": {}, "msg": "[MobiFlow] Storing MobiFlow record to SDL UE;1;1729716349154.0964;v2.0;SECSM;0;60786;1450744508;0;0;0;0;0;RRCSetup;2;0;0;0;1729716349154.0103;0;0;0"}
{"ts": 1729716349155, "crit": "INFO", "id": "ricxappframe.xapp_frame", "mdc": {}, "msg": "[MobiFlow] Storing MobiFlow record to SDL BS;2;1729716349154.1838;v2.0;SECSM;0;208;099;0;00bc614e;1000;1;0;0;1729716338046.782;0"}
{"ts": 1729716349156, "crit": "INFO", "id": "ricxappframe.xapp_frame", "mdc": {}, "msg": "[MobiFlow] Storing MobiFlow record to SDL UE;2;1729716349154.2026;v2.0;SECSM;0;60786;1450744508;0;0;0;0;0;RRCSetupComplete;2;0;0;0;1729716349154.0103;0;0;0"}
{"ts": 1729716349156, "crit": "INFO", "id": "ricxappframe.xapp_frame", "mdc": {}, "msg": "[MobiFlow] Storing MobiFlow record to SDL UE;3;1729716349154.2297;v2.0;SECSM;0;60786;1450744508;0;0;0;0;0;Registrationrequest;2;1;0;0;1729716349154.0103;0;1729716349154.0103;0"}
{"ts": 1729716349156, "crit": "INFO", "id": "ricxappframe.xapp_frame", "mdc": {}, "msg": "[MobiFlow] Storing MobiFlow record to SDL BS;3;1729716349154.2725;v2.0;SECSM;0;208;099;0;00bc614e;1000;1;0;0;1729716338046.782;0"}
...
```

## SDL Database

The MobiFlow telemetry will be stored in the SDL databased provided by the OSC RIC infrastructure. The Shared Data Layer (SDL) provides a lightweight, high-speed interface (API) for accessing shared data storage. SDL can be used for storing and sharing any data. Data can be shared at VNF level. One typical use case for SDL is sharing the state data of stateful application processes. Thus enabling stateful application processes to become stateless, conforming with, e.g., the requirements of the fifth generation mobile networks. Refer to: https://wiki.o-ran-sc.org/pages/viewpage.action?pageId=20874400

By default, the OSC near-RT RIC will deploy the redis database as a service backend.

```
$ sudo kubectl get pods -n ricplt
NAME                                                         READY   STATUS    RESTARTS   AGE
...
statefulset-ricplt-dbaas-server-0                            1/1     Running   0          100m
```

You may login to the SDL through:

```
kubectl exec -it statefulset-ricplt-dbaas-server-0 -n ricplt sh
```

Use the `sdlcli` command in the pod to lookup the stored MobiFlow data:

```
/data # sdlcli get namespaces
appdb
appmgr
bs_mobiflow
e2Manager
submgr_restSubsDb
ue_mobiflow
/data #
/data # sdlcli get ue_mobiflow 1
1:�iUE;1;1729716349154.0964;v2.0;SECSM;0;60786;1450744508;0;0;0;0;0;RRCSetup;2;0;0;0;1729716349154.0103;0;0;0
```

Other xApps deployed at the nRT-RIC can also use RESTFul APIs to access these data in the SDL. Refer to our other xApp examples such as [MobieXpert](https://github.com/5GSEC/MobieXpert/tree/osc) and [MobiWatch](https://github.com/5GSEC/MobiWatch) to checkout the implementation.


## Publication

Please cite our research papers if you develop any products and prototypes based on our code:

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


