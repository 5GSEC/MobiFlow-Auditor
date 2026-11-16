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


We also have an old version at branch `main` implemented for the [ONOS RIC](https://docs.onosproject.org/v0.6.0/onos-cli/docs/cli/onos_ric/) on [SD-RAN](https://docs.sd-ran.org/master/index.html). It was used as part of the [5G-Spector](https://github.com/5GSEC/5G-Spector) artifact but not recommended any more since the ONOS RIC xApp python SDK is no longer being maintained.


## MobiFlow Structure

The current MobiFlow message definition is defined in [mobiflow.py](./src/mobiflow/mobiflow.py#L60). It mainly collects (1) the fine-grained layer-3 (RRC and NAS) state transition information of UEs at the message level; (2) the aggregated flow-based statistics from the base stations. MobiFlow telemetry is reported over the E2SM-CP service model (below); E2SM-KPM (v2.0) carries 3GPP measurements only. 

### E2SM-CP (experimental)

MobiFlow Auditor also subscribes to **E2SM-CP** (OID `1.3.6.1.4.1.32473.1.1.2.1`), the MobiFlow control plane telemetry service model of the [5G-eBPF MobiFlow agent](https://github.com/5GSEC/5G-eBPF) (spec: `e2sm/e2sm-cp` there). Instead of KPM measurements reported periodically, an E2 node reports every observed control plane message (F1AP, with the RRC and NAS messages inside) as an event, grouped by UE connection, when it occurs.

- The RAN functions to subscribe to are listed by OID in `ran.target_oid_list` ([init/config-file.json](./init/config-file.json)); each is subscribed with the service model of its OID (exact match: `1.3.6.1.4.1.53148.1.2.2.2` E2SM-KPM, `1.3.6.1.4.1.32473.1.1.2.1` E2SM-CP; other OIDs are skipped with a warning). E2SM-CP RAN functions are subscribed with every report style and attribute they define.
- RIC indications are decoded at the E2AP layer by [IndicationHandler](./src/handler/IndicationHandler.py) and handed to [KpmIndicationHandler](./src/handler/KpmIndicationHandler.py) or [CpIndicationHandler](./src/handler/CpIndicationHandler.py) depending on the subscription's service model.
- E2SM-CP events are only logged for now (`[E2SM-CP]` lines); they are not stored in the SDL.
- E2SM-KPM carries only 3GPP measurements (TS 28.552, e.g. `RRC.ConnEstabAtt`), no MobiFlow telemetry: the xApp subscribes to every measurement of the first report style with action definition format 1 (E2 Node Measurement). The E2 node sends an indication every reporting period, with one record per granularity period: `ran.e2sm_kpm.reporting_period_ms` (event trigger) and `ran.e2sm_kpm.granularity_period_ms` (action definition), which must divide the reporting period. The measurements are only logged for now (`[E2SM-KPM]` lines).
- The E2SM-CP ASN.1 code is generated into `src/asn1/e2sm_cp` (`asn1_compile_cp.sh`) and built into its own wrapper, `src/asn1/wrapper_cp` (`wrapper_compile.sh`).
- `tests/e2_replay/replay.py` replays E2AP PDUs recorded from the agent (E2SM-CP and E2SM-KPM) through the xApp code, without a RIC, and prints the log.

### RAN configuration

The `ran` section of [init/config-file.json](./init/config-file.json) configures the subscriptions ([src/utils/config.py](./src/utils/config.py)). Every key is optional and takes the default below when missing. A wrong type or an out-of-range value stops the xApp at startup, with the key named in the log; an unknown key is logged as a warning and ignored.

| Key | Default | Meaning |
| --- | --- | --- |
| `target_oid_list` | both OIDs above | RAN functions to subscribe to, by OID; unsupported OIDs are ignored with a warning |
| `poll_interval_ms` | `5000` | How often the R-NIB is polled for E2 nodes, i.e. how soon a new or reconnected node is subscribed to (min `100`) |
| `e2sm_kpm.reporting_period_ms` | `1000` | E2SM-KPM indication period (event trigger) |
| `e2sm_kpm.granularity_period_ms` | the reporting period | E2SM-KPM measurement record period (action definition); must divide the reporting period |
| `e2sm_cp.max_batch_size` | `0` | E2SM-CP: report once this many events are pending (`0`: no limit, `1..65535`) |
| `e2sm_cp.max_batch_delay_ms` | `0` | E2SM-CP: report once this long has elapsed since the first pending event (`0`: no limit) |

With both E2SM-CP limits at `0`, each event is reported in its own indication as it occurs. The settings apply to subscriptions made after the xApp starts; the config file is read from the image (`/tmp/init/config-file.json`), so a change needs a rebuild.




## Prerequisite

### Local Docker registry

MobiFlow-Auditor is built from source as a local Docker container. Refer to the official tutorial (https://docs.docker.com/engine/install/) to install and set up the Docker environment.

Create a local docker registry to host docker images: 

```
sudo docker run -d -p 5000:5000 --restart=always --name registry registry:2
```

### OSC nearRT RIC

Before deploying the xApp, make sure the OSC nRT-RIC is deployed by following this [tutorial](https://github.com/5GSEC/5G-Spector/wiki/O%E2%80%90RAN-SC-RIC-Deployment-Guide#deploy-the-osc-near-rt-ric).


## Build the MobiFlow-Auditor xApp

Simply run our build script:

```
./build.sh
```

After a successful build, the xApp will be compiled as a standalone Docker container.

```
$ docker images
REPOSITORY                         TAG       IMAGE ID       CREATED          SIZE
localhost:5000/mobiflow-auditor    0.0.1     c6312eb0d32e   2 minutes ago    237M
```


## Install / Uninstall the xApp

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

### Step 1. Deploy the OSC nRT RIC

Deploy the OSC nRT-RIC and make sure it is running properly following this [tutorial](https://github.com/5GSEC/5G-Spector/wiki/O%E2%80%90RAN-SC-RIC-Deployment-Guide#deploy-the-osc-near-rt-ric)

### Step 2. Deploy the OAI gNB

Next, deploy the OAI gNB that connects to the nRT-RIC through the E2 interface. You can refer to our [tutorial](https://github.com/5GSEC/5G-Spector/wiki/O%E2%80%90RAN-SC-RIC-Deployment-Guide#connect-oai-gnb-to-osc-ric) to deploy the OAI gNB which is extended with the E2 agent we have implemented. Ensure the gNB is up and connected to the RIC.
Make sure the gNB's E2 interface IP points to the nRT-RIC's E2T pod.

### Step 3. Run the MobiFlow Auditor xApp

Run the MobiFlow Auditor xApp (assuming the image has been built):

```
./deploy.sh
```

The xApp will recognize the gNB and starts a subscription with it through the E2SM KPM service model.

### Step 4. Start the OAI nrUE to generate traffic

Finally, run the OAI nrUE (or a commercial UE) to attach to the gNB and generate 5G traffic. We have provided instructions on how to run the OAI UE at this [link](https://github.com/5GSEC/5G-Spector/wiki/O%E2%80%90RAN-SC-RIC-Deployment-Guide#run-oai-ue).

### Step 5. Examine the MobiFlow data

By running the MobiFlow Auditor on the RIC along with an OAI gNB and nrUE, MobiFlow Auditor will generate and store MobiFlow telemetry. You can check the run-time logs with:

```
./log.sh
```

Example log entries from the xApp:

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


