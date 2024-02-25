import argparse
import json
import time
import grpc
import logging
import asyncio
from concurrent import futures
from typing import Any, Dict
from secsm.rpc.server import MobiFlowService
from secsm.rpc.protos.mobiflow_service_pb2_grpc import add_MobiFlowQueryServicer_to_server

rpc_server = None

async def start_rpc_server(db_path, rpc_port):
    global rpc_server
    logging.info(f"[RPC Server] Server starting, listening on {rpc_port}")
    rpc_server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_MobiFlowQueryServicer_to_server(MobiFlowService(db_path), rpc_server)
    rpc_server.add_insecure_port(f"0.0.0.0:{rpc_port}")
    rpc_server.start()
    # rpc_server.wait_for_termination()

    try:
        # Keep the server running until terminated
        await asyncio.Future()  # This future never resolves, effectively keeping the event loop running
    except asyncio.CancelledError:
        rpc_server.stop(0)
        logging.info("[RPC Server] Server stopped")

async def init_global(mobiflow_config: Dict[str, Any]):
    # load configs
    db_path = mobiflow_config["mobiflow"]["sqlite3_db_path"]
    rpc_port = int(mobiflow_config["mobiflow"]["rpc_port"])
    csv_file = mobiflow_config["pbest"]["pbest_csv_file"]
    # Start rpc server
    await start_rpc_server(db_path, rpc_port)

async def async_main(args):
    with open(args.mobiflow_config) as f:
        mobiflow_config = json.load(f)
        rpc_task = asyncio.create_task(init_global(mobiflow_config))
        await rpc_task

    while True:
        time.sleep(500) # Loop

if __name__ == "__main__":
    logging.basicConfig(
        format="%(levelname)s %(asctime)s %(filename)s:%(lineno)d] %(message)s",
        level=logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    parser = argparse.ArgumentParser(description="MobiFlow Auditor xApp.")
    parser.add_argument("--mobiflow-config", type=str, help="mobiflow config")
    args = parser.parse_args()

    asyncio.run(async_main(args))

