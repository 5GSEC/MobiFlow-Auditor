#!/usr/bin/env python3
# SPDX-FileCopyrightText: Copyright 2004-present Facebook. All Rights Reserved.
# SPDX-FileCopyrightText: 2019-present Open Networking Foundation <info@opennetworking.org>
#
# SPDX-License-Identifier: Apache-2.0

import asyncio
import logging
import time
import threading
from typing import Any, Dict

import betterproto
import onos_ric_sdk_py as sdk
from onos_api.e2t.e2.v1beta1 import (
    Action,
    ActionType,
    SubsequentAction,
    SubsequentActionType,
    TimeToWait,
)
from onos_api.topo import (
    E2Node,
    KpmReportStyle,
    ServiceModelInfo,
)
from onos_e2_sm.e2smkpmv2.v2 import (
    CellObjectId,
    E2SmKpmActionDefinition,
    E2SmKpmActionDefinitionFormat1,
    E2SmKpmEventTriggerDefinition,
    E2SmKpmEventTriggerDefinitionFormat1,
    E2SmKpmIndicationHeader,
    E2SmKpmIndicationMessage,
    GranularityPeriod,
    MeasurementInfoItem,
    MeasurementInfoList,
    MeasurementType,
    MeasurementTypeName,
    RicStyleType,
    SubscriptionId,
)

from .metrics import CUSTOM_COLLECTOR
from .encoding import *
from .mobiflow import *
from .factbase import *
from .mobiflow_writer import *

KPM_SERVICE_MODEL_OID_V2 = "1.3.6.1.4.1.53148.1.2.2.2"

# Global vars
fb = FactBase()
lock = threading.Lock()
mf_writer = None

def init_global(mobiflow_config: Dict[str, Any]):
    # load configs
    db_name = mobiflow_config["mobiflow"]["mongo_db_name"]
    db_port = int(mobiflow_config["mobiflow"]["mongo_db_port"])
    csv_file = mobiflow_config["pbest"]["pbest_csv_file"]
    pbest_exec_name = mobiflow_config["pbest"]["pbest_exec_name"]
    pbest_log_path = mobiflow_config["pbest"]["pbest_log_path"]
    maintenance_time_threshold = int(mobiflow_config["pbest"]["maintenance_time_threshold"])
    # Init mobiflow writer configs
    global mf_writer
    mf_writer = MobiFlowWriter(csv_file, db_name, db_port)

async def subscribe(
    app_config: Dict[str, Any],
    e2_client: sdk.E2Client,
    sdl_client: sdk.SDLClient,
    e2_node_id: str,
    e2_node: E2Node,
    report_style: KpmReportStyle,
) -> None:
    # Save subscription ID -> cell global ID for Prometheus metric labeling
    sub_map = {}

    # Sort cell IDs to create identical, deterministic subscriptions for demo
    actions = []
    for idx, cell in enumerate(
        sorted(await sdl_client.get_cells(e2_node_id), key=lambda c: c.cell_object_id)
    ):
        meas_info_list = MeasurementInfoList()
        for measurement in report_style.measurements:
            meas_id = measurement.id
            if type(meas_id) is str:
                meas_id = int(measurement.id.replace("value:", ""))
            CUSTOM_COLLECTOR.register(meas_id, measurement.name)
            meas_info_list.value.append(
                MeasurementInfoItem(
                    meas_type=MeasurementType(
                        meas_name=MeasurementTypeName(value=measurement.name)
                    )
                )
            )
        # parse new BS information
        cell_global_id = cell.cell_global_id.value
        bs_name = e2_node_id + "_" + cell_global_id
        sub_map[idx + 1] = cell_global_id
        # construct mcc and mnc from plmnid
        mcc = 0
        mnc = 0
        # add new BS record
        logging.info("Adding new BS: %s" % bs_name)
        report_period = app_config["report_period"]["granularity"]
        bs = BS()
        bs.bs_id = -1  # indicate a new BS
        bs.cell_id = cell_global_id
        bs.name = bs_name
        bs.mcc = mcc
        bs.mnc = mnc
        bs.report_period = report_period
        # only allow one thread to update fact base
        lock.acquire()
        fb.add_bs(bs)
        lock.release()

        if mf_writer is not None:
            mf_writer.write_mobiflow(fb)
        action_def = E2SmKpmActionDefinition(
            ric_style_type=RicStyleType(value=report_style.type),
        )
        action_def.action_definition_formats.action_definition_format1=E2SmKpmActionDefinitionFormat1(
            cell_obj_id=CellObjectId(value=cell.cell_object_id),
            meas_info_list=meas_info_list,
            granul_period=GranularityPeriod(
                value=app_config["report_period"]["granularity"]
            ),
            subscript_id=SubscriptionId(value=idx + 1),
        )
        action = Action(
            id=idx,
            type=ActionType.ACTION_TYPE_REPORT,
            subsequent_action=SubsequentAction(
                type=SubsequentActionType.SUBSEQUENT_ACTION_TYPE_CONTINUE,
                time_to_wait=TimeToWait.TIME_TO_WAIT_ZERO,
            ),
            payload=bytes(
                action_def
            ),
        )
        actions.append(
            action
        )

    if not actions:
        logging.warning(f"No cells found for E2 node with ID: '{e2_node_id}'")
        return

    trigger_def = E2SmKpmEventTriggerDefinition()
    trigger_def.event_definition_formats.event_definition_format1=E2SmKpmEventTriggerDefinitionFormat1(
        reporting_period=app_config["report_period"]["interval"]
    )

    async for (header, message) in e2_client.subscribe(
        e2_node_id=e2_node_id,
        service_model_name="oran-e2sm-kpm",
        service_model_version="v2",
        subscription_id=f"fb-kpimon_oran-e2sm-kpm_sub_{e2_node_id}",
        trigger=bytes(trigger_def),
        actions=actions,
    ):
        # use lock to make sure the update order
        lock.acquire()
        logging.debug(f"raw header: {header}")
        logging.debug(f"raw message: {message}")

        ind_header = E2SmKpmIndicationHeader()
        ind_header.parse(header)
        ts = int.from_bytes(
            ind_header.indication_header_formats.indication_header_format1.collet_start_time.value, "big"
        )

        ind_message = E2SmKpmIndicationMessage()
        ind_message.parse(message)
        subscript_id = ind_message.indication_message_formats.indication_message_format1.subscript_id.value

        cellid = sub_map[subscript_id]
        bs_name = e2_node_id + "_" + cellid
        meas_info_list = ind_message.indication_message_formats.indication_message_format1.meas_info_list.value
        for meas_data_item in ind_message.indication_message_formats.indication_message_format1.meas_data.value:
            ue = UE()
            for idx, meas_record_item in enumerate(meas_data_item.meas_record.value):
                _, metric_value = betterproto.which_one_of(
                    meas_record_item, "measurement_record_item"
                )
                if metric_value is None:
                    logging.warning("Got a measurement record item with unset value")
                    continue

                _, type_value = betterproto.which_one_of(
                    meas_info_list[idx].meas_type, "measurement_type"
                )
                if type_value is None:
                    logging.warning("Got a measurement with unset type")
                    continue

                metric_family = CUSTOM_COLLECTOR.metrics.get(type_value.value)
                if metric_family is None:
                    logging.warning(f"No metric family found for '{type_value.value}'")
                    continue

                #logging.info(f"{metric_family.name}{{nodeid={e2_node_id}, cellid={cellid}}} {metric_value} {ts}")

                # SECSM: process received data
                if "rnti" in metric_family.name:
                    if metric_value == 0:
                        break  # don't display log for empty record

                if not "msg" in metric_family.name:
                    if "rnti" in metric_family.name:
                        ue.rnti = metric_value
                    elif "imsi1" in metric_family.name:
                        ue.imsi = metric_value
                    elif "imsi2" in metric_family.name:
                        ue.imsi = ue.imsi + (metric_value << 32)
                    elif "tmsi" in metric_family.name:
                        ue.tmsi = metric_value
                    elif "cipher_alg" in metric_family.name:
                        ue.cipher_alg = metric_value
                    elif "integrity_alg" in metric_family.name:
                        ue.integrity_alg = metric_value
                    elif "establish_cause" in metric_family.name:
                        ue.establish_cause = metric_value
                    elif "emm_cause" in metric_family.name:
                        ue.emm_cause = metric_value
                    elif "rat" in metric_family.name:
                        ue.rat = metric_value
                    #logging.info(f"Metadata: {metric_family.name}: {{nodeid={e2_node_id}, cellid={cellid}}} {metric_value} {ts}")
                elif metric_value & 1 == 1:
                    # RRC
                    dcch = (metric_value >> 1) & 1
                    downlink = (metric_value >> 2) & 1
                    msg_id = (metric_value >> 3)
                    msg_name = decode_rrc_msg(dcch, downlink, msg_id, ue.rat)
                    if msg_name != "" and msg_name is not None:
                        ue.msg_trace.append(msg_name)
                    elif msg_id != 0:
                        logging.error(f"Invalid RRC Msg {metric_family.name}: dcch={dcch}, downlink={downlink} {msg_id} {ts}")
                    #logging.info(f"RRC: {metric_family.name}: {{nodeid={e2_node_id}, cellid={cellid}}} {msg_name} {ts}")

                else:
                    # NAS
                    dis = (metric_value >> 1) & 1
                    msg_id = (metric_value >> 2)
                    msg_name = decode_nas_msg(dis, msg_id, ue.rat)
                    if msg_name != "" and msg_name is not None:
                        ue.msg_trace.append(msg_name)
                    elif msg_id != 0:
                        logging.error(f"Invalid NAS Msg: {metric_family.name}: discriminator={dis} {msg_id} {ts}")
                    #logging.info(f"NAS: {metric_family.name}: {{nodeid={e2_node_id}, cellid={cellid}}} {msg_name} {ts}")

                metric_family.add_metric(
                    labels=[e2_node_id, cellid],
                    value=metric_value,
                    timestamp=ts,
                )
            # update ue record in BS
            if ue.rnti == 0:
                continue  # ignore empty ue record

            fb.add_ue(fb.get_bs_index_by_name(bs_name), ue)
            #logging.info("======================New SecSM Event========================")
            #logging.info(fb.get_bs(bs_id))
            #logging.info(ue)
            #logging.info("======================End SecSM Event========================")
            if mf_writer is not None:
                mf_writer.write_mobiflow(fb)
        # thread finish processing all records, relaese lock
        lock.release()

async def run(
    app_config: Dict[str, Any],
    e2_client: sdk.E2Client,
    sdl_client: sdk.SDLClient,
    e2_node_id: str,
    e2_node: E2Node,
    service_model: ServiceModelInfo,
) -> None:
    subscriptions = []
    for report_style in service_model.ran_functions[0].report_styles:
        subscriptions.append(
            subscribe(
                app_config, e2_client, sdl_client, e2_node_id, e2_node, report_style
            )
        )

    await asyncio.gather(*subscriptions)

