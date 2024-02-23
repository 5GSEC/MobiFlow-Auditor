<!--
SPDX-FileCopyrightText: Copyright 2004-present Facebook. All Rights Reserved.
SPDX-FileCopyrightText: 2019-present Open Networking Foundation <info@opennetworking.org>

SPDX-License-Identifier: Apache-2.0
-->

# MobiFlow-Auditor-xApp

MobiFlow Auditor is an O-RAN compliant xApp aiming to support ***fine-grained and security-aware statistics monitoring over the RAN data plane***, which is not solved by the default O-RAN standard and service models. We abstract such telemetry streams as **MobiFlow**, a novel security audit trail for holding mobile devices accountable during the link and session setup protocols as they interact with the base station, and interval statistics generated for tracking large-scale patterns of abuse against the base station.

MobiFlow Auditor can drive various analyses. For example, it can drive expert system analysis with [MobiExpert](https://github.com/5GSEC/MobieXpert). MobiExpert xApp allows network operators to program stateful production-based IDS rules for detecting a wide range of cellular L3 attacks. It features the Production-Based Expert System Toolset ([P-BEST](https://ieeexplore.ieee.org/document/766911)) language. MobiFlow Auditor can also drive AI / ML-based analytics. 

To learn more about the format and structure of MobiFlow, please refer to our papers:

- [A Fine-Grained Telemetry Stream for Security Services in 5G Open Radio Access Networks](https://dl.acm.org/doi/abs/10.1145/3565474.3569070) (EmergingWireless'22)
- [5G-Spector: An O-RAN Compliant Layer-3 Cellular Attack Detection Service](https://web.cse.ohio-state.edu/~wen.423/papers/5G-Spector-NDSS24.pdf) (NDSS'24)




## Prerequisite

MobiFlow-Auditor is built as a Docker container. Refer to the official tutorial (https://docs.docker.com/engine/install/) to install and set up the Docker environment.

Create a local docker registry to host docker images: 

```
sudo docker run -d -p 5000:5000 --restart=always --name registry registry:2
```

## Architecture

The current implementation of MobiFlow Auditor is dedicated to the [ONOS RIC](https://docs.onosproject.org/v0.6.0/onos-cli/docs/cli/onos_ric/) on [SD-RAN](https://docs.sd-ran.org/master/index.html) and OpenAirInterface5G (https://gitlab.eurecom.fr/oai/openairinterface5g/).

Its communication with the RAN nodes (via E2) is based on the [ONOS RIC's python SDK](https://github.com/onosproject/onos-ric-sdk-py) and guidance from the exemplar [ONOS RAN Intelligent Controller xApps](https://github.com/onosproject/onos-ric-python-apps/) authored in Python programming language.

MobiFlow Auditor's data can be accessed by other analytic xApps through [gRPC](https://grpc.io/docs/languages/python/). The RPC API definitions can be found at [mobiflow_service.proto](https://github.com/5GSEC/MobiFlow-Auditor/blob/main/mobiflow-auditor/secsm/rpc/protos/mobiflow_service.proto).



## MobiFlow Structure

The current MobiFlow message definition is defined in [mobiflow.py](https://github.com/5GSEC/MobiFlow-Auditor/blob/main/mobiflow-auditor/secsm/mobiflow/mobiflow.py). It mainly collects (1) the fine-grained layer-3 (RRC and NAS) state transition information of UEs at the message level; (2) the aggregated flow-based statistics from the base stations.

The MobiFlow telemetry report process is based on the E2SM-KPM (v2.0) service model (SM). The E2SM implementation can be found at https://github.com/onosproject/onos-e2-sm.

MobiFlow Auditor xApp requires O-RAN compliant RAN nodes to collect and report corresponding data. We have augmented the OpenAirInterface with MobiFlow telemetry support at [https://github.com/onehouwong/OAI-5G](https://github.com/5GSEC/OAI-5G) branch `2023.w23.secsm.sdran`.


## Build the MobiFlow-Auditor xApp

```
./build.sh
```

After a successful build, the xApp will be compiled as a standalone Docker container.

```
$ docker images
REPOSITORY                           TAG       IMAGE ID       CREATED          SIZE
localhost:5000/mobiflow-auditor      latest    4842d1672817   26 minutes ago   218MB
```


## Install the MobiFlow-Auditor xApp

We have provided a default helm chart for deploying MobiFlow-Auditor on the ONOS RIC via [Kubernetes](https://kubernetes.io/) and [Helm](https://helm.sh/).

```
./install_xapp.sh
```

Make sure the xApp is up and running:

```
$ kubectl get pods -n riab
NAME                                READY   STATUS    RESTARTS   AGE
mobiflow-auditor-68d598d7fb-vhlqw   3/3     Running   0          4m10s
...
```

## Example output

By running the MobiFlow Auditor on the RIC along with an OAI gNB and nrUE, MobiFlow Auditor will generate and store MobiFlow telemetry. You can check the run-time logs with:

```
$ kubectl logs mobiflow-auditor-68d598d7fb-vhlqw -n riab -c mobiflow-auditor
INFO 2024-01-26 21:04:28 web_log.py:206] 192.168.121.113 [26/Jan/2024:21:04:28 +0000] "GET /status HTTP/1.1" 200 180 "-" "kube-probe/1.23"
INFO 2024-01-26 21:04:35 onos_ric_secsm.py:106] Adding new BS: e2:1/e00_e0000
INFO 2024-01-26 21:04:35 mobiflow_writer.py:162] [MobiFlow] Writing BS Mobiflow to DB: INSERT INTO bs_mobiflow (msg_type, msg_id, timestamp, mobiflow_ver, generator_name, bs_id, mcc, mnc, tac, cell_id, report_period, connected_ue_cnt, idle_ue_cnt, max_ue_cnt, initial_timer, inactive_timer) VALUES ('BS', 0, 1706303075078.2427, 'v2.0', 'SECSM', 0, 0, 0, 0, 'e0000', 1000, 0, 0, 0, 1706303075078.195, 0);
......
INFO 2024-01-26 21:04:55 mobiflow_writer.py:147] [MobiFlow] Writing UE Mobiflow to DB: INSERT INTO ue_mobiflow (msg_type, msg_id, timestamp, mobiflow_ver, generator_name, bs_id, rnti, tmsi, imsi, imei, cipher_alg, integrity_alg, establish_cause, msg, rrc_state, nas_state, sec_state, emm_cause, rrc_initial_timer, rrc_inactive_timer, nas_initial_timer, nas_inactive_timer) VALUES ('UE', 0, 1706303095525.7058, 'v2.0', 'SECSM', 0, 40182, 0, 0, 0, 0, 0, 3, 'RRCSetupRequest', 0, 0, 0, 0, 0, 0, 0, 0);
INFO 2024-01-26 21:04:55 mobiflow_writer.py:147] [MobiFlow] Writing UE Mobiflow to DB: INSERT INTO ue_mobiflow (msg_type, msg_id, timestamp, mobiflow_ver, generator_name, bs_id, rnti, tmsi, imsi, imei, cipher_alg, integrity_alg, establish_cause, msg, rrc_state, nas_state, sec_state, emm_cause, rrc_initial_timer, rrc_inactive_timer, nas_initial_timer, nas_inactive_timer) VALUES ('UE', 1, 1706303095695.7827, 'v2.0', 'SECSM', 0, 40182, 0, 0, 0, 0, 0, 3, 'RRCSetup', 2, 0, 0, 0, 1706303095525.6619, 0, 0, 0);
INFO 2024-01-26 21:04:55 mobiflow_writer.py:162] [MobiFlow] Writing BS Mobiflow to DB: INSERT INTO bs_mobiflow (msg_type, msg_id, timestamp, mobiflow_ver, generator_name, bs_id, mcc, mnc, tac, cell_id, report_period, connected_ue_cnt, idle_ue_cnt, max_ue_cnt, initial_timer, inactive_timer) VALUES ('BS', 1, 1706303095808.877, 'v2.0', 'SECSM', 0, 0, 0, 0, 'e0000', 1000, 1, 0, 0, 1706303075078.195, 0);
INFO 2024-01-26 21:04:56 mobiflow_writer.py:147] [MobiFlow] Writing UE Mobiflow to DB: INSERT INTO ue_mobiflow (msg_type, msg_id, timestamp, mobiflow_ver, generator_name, bs_id, rnti, tmsi, imsi, imei, cipher_alg, integrity_alg, establish_cause, msg, rrc_state, nas_state, sec_state, emm_cause, rrc_initial_timer, rrc_inactive_timer, nas_initial_timer, nas_inactive_timer) VALUES ('UE', 2, 1706303096003.0918, 'v2.0', 'SECSM', 0, 40182, 0, 0, 0, 0, 0, 3, 'RRCSetupComplete', 2, 0, 0, 0, 1706303095525.6619, 0, 0, 0);
INFO 2024-01-26 21:04:56 mobiflow_writer.py:147] [MobiFlow] Writing UE Mobiflow to DB: INSERT INTO ue_mobiflow (msg_type, msg_id, timestamp, mobiflow_ver, generator_name, bs_id, rnti, tmsi, imsi, imei, cipher_alg, integrity_alg, establish_cause, msg, rrc_state, nas_state, sec_state, emm_cause, rrc_initial_timer, rrc_inactive_timer, nas_initial_timer, nas_inactive_timer) VALUES ('UE', 3, 1706303096133.8472, 'v2.0', 'SECSM', 0, 40182, 0, 0, 0, 0, 0, 3, 'Registrationrequest', 2, 1, 0, 0, 1706303095525.6619, 0, 1706303095525.6619, 0);
INFO 2024-01-26 21:04:56 mobiflow_writer.py:162] [MobiFlow] Writing BS Mobiflow to DB: INSERT INTO bs_mobiflow (msg_type, msg_id, timestamp, mobiflow_ver, generator_name, bs_id, mcc, mnc, tac, cell_id, report_period, connected_ue_cnt, idle_ue_cnt, max_ue_cnt, initial_timer, inactive_timer) VALUES ('BS', 2, 1706303096233.8115, 'v2.0', 'SECSM', 0, 0, 0, 0, 'e0000', 1000, 1, 0, 0, 1706303075078.195, 0);
...
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
