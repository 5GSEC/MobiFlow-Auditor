import grpc
import mobiflow_service_pb2_grpc
import mobiflow_service_pb2
import time

def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = mobiflow_service_pb2_grpc.MobiFlowQueryStub(channel)

        while True:
            response = stub.MobiFlowQuery(mobiflow_service_pb2.MobiFlowQueryRequest(name="mobi-expert", table="bs_mobiflow"))
            print(f"Read data from Program 1's database: Value='{response.message}'")
            time.sleep(5)  # Adjust the interval as needed


if __name__ == '__main__':
    run()
