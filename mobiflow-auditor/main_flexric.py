import time
import logging
import pathlib
import argparse
import json
from secsm.PBest import PBest
import sys
sys.path.append('../../')
import xapp_sdk as ric

# Create a callback for NEW which derived it from C++ class new_cb
# class SecSmCallback(ric.new_cb):
#     def __init__(self):
#         # Inherit C++ new_cb class
#         ric.new_cb.__init__(self)
#
#     # Create an override C++ method
#     def handle(self, ind):
#         if len(ind.rb_stats) > 0:
#             t_now = time.time_ns() / 1000.0
#             t_new = ind.tstamp / 1.0
#             t_diff = t_now - t_new
#             print('new Indication tstamp = ' + str(ind.tstamp) + ' diff = ' + str(t_diff))


def main(args: argparse.Namespace) -> None:
    config = json.loads(pathlib.Path(args.ric_config).read_text())
    report_interval = config["report_config"]["interval"]

    logging.info(f'Report Interval: {report_interval}')

    # init ric component
    ric_address = config["ric_config"]["ric_address"]
    ric_port = config["ric_config"]["ric_port"]
    ric.init()

    # listen to RIC subscriptions
    conn = ric.conn_e2_nodes()
    assert(len(conn) > 0)
    for i in range(0, len(conn)):
        # conn[i] is e2_node_connected_t
        # pull basic node info
        type = conn[i].id.type
        cell_id = conn[i].id.nb_id
        print(f"Type {type}")
        print(f"ID {cell_id}")
        print("Global E2 Node [" + str(i) + "]: PLMN MCC = " + str(conn[i].id.plmn.mcc))
        print("Global E2 Node [" + str(i) + "]: PLMN MNC = " + str(conn[i].id.plmn.mnc))

        # query supported service model
        ran_func = conn[i].ran_func
        ran_func_len = len(ran_func)
        print(ran_func)
        print(ran_func_len)

    # for i in range(0, len(conn)):
    #     secsm_cb = SecSmCallback()
    #     ric.report_sm_xapp_api(conn[i].id, ric.SM_KPM_ID, secsm_cb)
    #     time.sleep(report_interval/1000)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="secsm xApp.")
    parser.add_argument(
        "--path", type=str, help="path to the service's JSON configuration file"
    )
    parser.add_argument(
        "--ric-config",
        type=str,
        help="xApp module config",
        default="config.json",
    )
    args = parser.parse_args()
    main(args)

