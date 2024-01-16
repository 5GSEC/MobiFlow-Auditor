import argparse
import json
import grpc
import logging
import threading
from concurrent import futures
from typing import Any, Dict
from secsm.rpc.server import MobiFlowService
from secsm.rpc.protos.mobiflow_service_pb2_grpc import add_MobiFlowQueryServicer_to_server

rpc_server = None

def start_rpc_server(db_path, rpc_port):
    global rpc_server
    logging.info(f"[RPC Server] Server starting, listening on {rpc_port}")
    rpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_MobiFlowQueryServicer_to_server(MobiFlowService(db_path), rpc_server)
    rpc_server.add_insecure_port(f"0.0.0.0:{rpc_port}")
    rpc_server.start()
    rpc_server.wait_for_termination()

def init_global(mobiflow_config: Dict[str, Any]):
    # load configs
    db_path = mobiflow_config["mobiflow"]["sqlite3_db_path"]
    rpc_port = int(mobiflow_config["mobiflow"]["rpc_port"])
    csv_file = mobiflow_config["pbest"]["pbest_csv_file"]
    pbest_exec_name = mobiflow_config["pbest"]["pbest_exec_name"]
    pbest_log_path = mobiflow_config["pbest"]["pbest_log_path"]
    maintenance_time_threshold = int(mobiflow_config["pbest"]["maintenance_time_threshold"])
    # Start rpc server
    global rpc_thread
    rpc_thread = threading.Thread(target=start_rpc_server, args=(db_path, rpc_port))
    rpc_thread.start()

if __name__ == "__main__":
    logging.basicConfig(
        format="%(levelname)s %(asctime)s %(filename)s:%(lineno)d] %(message)s",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    parser = argparse.ArgumentParser(description="MobiFlow Auditor xApp.")
    parser.add_argument("--mobiflow-config", type=str, help="mobiflow config")
    args = parser.parse_args()

    with open(args.mobiflow_config) as f:
        mobiflow_config = json.load(f)

    init_global(mobiflow_config)



