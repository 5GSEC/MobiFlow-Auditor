import sqlite3
import logging
from protos.mobiflow_service_pb2_grpc import MobiFlowQueryServicer
from protos.mobiflow_service_pb2 import MobiFlowQueryResponse

class MobiFlowService(MobiFlowQueryServicer):
    def __init__(self, db_path, rpc_port=50051):
        self.db_path = db_path
        self.rpc_port = rpc_port
        self.db = None
        if self.db_path is not None and self.db_path != "":
            self.init_db_conn()

    def init_db_conn(self):
        # Connect to SQLite database (local.db)
        self.db = sqlite3.connect(self.db_path)

    def get_db_cursor(self):
        return self.db.cursor()

    def mobiflow_query_response(self, request, context):
        request_initiator = request.name
        request_table = request.table

        logging.info(f"[Server] Request received from {request_initiator} regarding {request_table}")

        # Read the latest data from the database
        cursor = self.get_db_cursor()
        cursor.execute(f'SELECT * FROM {request_table} ORDER BY timestamp DESC LIMIT 1')
        result = cursor.fetchone()

        if result:
            _id, value, timestamp = result
            return MobiFlowQueryResponse(value=value, timestamp=str(timestamp))
        else:
            return MobiFlowQueryResponse(value="No data available", timestamp="")

