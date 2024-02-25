import sqlite3
import logging
import asyncio
from .protos.mobiflow_service_pb2_grpc import MobiFlowQueryServicer
from .protos.mobiflow_service_pb2 import MobiFlowStreamResponse

class MobiFlowService(MobiFlowQueryServicer):
    def __init__(self, db_path, rpc_port=50051):
        self.db_path = db_path
        self.rpc_port = rpc_port
        self.MOBIFLOW_DELIMITER = ";"
        self.client_last_record = {}  # a dict to track the last MobiFlow record each client has read

    def open_db_conn(self):
        # Connect to SQLite database (local.db)
        if self.db_path is not None and self.db_path != "":
            return sqlite3.connect(self.db_path, check_same_thread=False)
        else:
            logging.error(f"[Server] Invalid DB Path {self.db_path}")
            return None

    async def fetchall_async(self, conn, query):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, lambda: conn.cursor().execute(query).fetchall())

    def MobiFlowStream(self, request, context):
        request_initiator = request.name
        request_table = request.table

        last_id = -1
        try:
            last_id = self.client_last_record[request_initiator][request_table]
        except KeyError:
            if request_initiator not in self.client_last_record.keys():
                self.client_last_record[request_initiator] = {}
            self.client_last_record[request_initiator][request_table] = -1  # init if not found

        logging.info(f"[Server] MobiFlow Streaming Request from {request_initiator} for {request_table} last index {last_id}")

        # Read data from the database
        db = self.open_db_conn()
        if db is None:
            logging.error(f"[Server] DB instance is NULL, exiting...")
            return

        query_res = db.cursor().execute(f'SELECT * FROM {request_table} WHERE msg_id > ?', (last_id,)).fetchall()
        # query_res = await self.fetchall_async(db, query_stmt)
        for row in query_res:
            str_list = [str(a) for a in row]
            self.client_last_record[request_initiator][request_table] = int(str_list[1])  # update with latest msg_id
            msg = str(self.MOBIFLOW_DELIMITER.join(str_list))
            yield MobiFlowStreamResponse(message=msg)

