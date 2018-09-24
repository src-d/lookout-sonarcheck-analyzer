#!/usr/bin/env python3

# Analyzer that wrapps https://github.com/bblfsh/sonar-checks

from concurrent.futures import ThreadPoolExecutor

import os
import time
import grpc
import collections

from lookout.sdk import service_analyzer_pb2_grpc
from lookout.sdk import service_analyzer_pb2
from lookout.sdk import service_data_pb2_grpc
from lookout.sdk import service_data_pb2
from bblfsh_sonar_checks import (
        run_checks, list_checks, list_langs
)

from bblfsh import filter as filter_uast

host_to_bind = os.getenv('SONARCHECK_HOST', "0.0.0.0")
port_to_listen = os.getenv('SONARCHECK_PORT', 2022)
data_srv_addr = os.getenv('SONARCHECK_DATA_SERVICE_URL', "localhost:10301")
log_level = os.getenv('SONARCHECK_LOG_LEVEL', "info")

version = "alpha"
#TODO(bzz): add CLI arg
grpc_max_msg_size = 100 * 1024 * 1024 #100mb

class Analyzer(service_analyzer_pb2_grpc.AnalyzerServicer):
    def NotifyReviewEvent(self, request, context):
        print("got review request {}".format(request))

        # client connection to DataServe
        channel = grpc.insecure_channel(data_srv_addr, options=[
                ("grpc.max_send_message_length", grpc_max_msg_size),
                ("grpc.max_receive_message_length", grpc_max_msg_size),
            ])
        stub = service_data_pb2_grpc.DataStub(channel)
        changes = stub.GetChanges(
            service_data_pb2.ChangesRequest(
                head=request.commit_revision.head,
                base=request.commit_revision.base,
                want_contents=False,
                want_uast=True,
                exclude_vendored=True))

        comments = []
        for change in changes:
            print("analyzing '{}' in {}".format(change.head.path, change.head.language))
            check_results = run_checks(
                list_checks(change.head.language.lower()),
                change.head.language.lower(),
                change.head.uast
            )
            n = 0
            for check in check_results:
                for res in check_results[check]:
                    comments.append(
                        service_analyzer_pb2.Comment(
                            file=change.head.path,
                            line=res["pos"]["line"] if res and "pos" in res and res["pos"] and "line" in res["pos"] else 0,
                            text="{}: {}".format(check, res["msg"])))
                    n += 1
        print("{} comments produced".format(n))
        return service_analyzer_pb2.EventResponse(analyzer_version=version, comments=comments)

    def NotifyPushEvent(self, request, context):
        pass

def serve():
    server = grpc.server(thread_pool=ThreadPoolExecutor(max_workers=10))
    service_analyzer_pb2_grpc.add_AnalyzerServicer_to_server(Analyzer(), server)
    server.add_insecure_port("{}:{}".format(host_to_bind, port_to_listen))
    server.start()

    one_day_sec = 60*60*24
    try:
        while True:
            time.sleep(one_day_sec)
    except KeyboardInterrupt:
        server.stop(0)


def print_check_stats():
    num_checks = 0
    all_checks = collections.defaultdict(list)
    langs = list_langs()
    for lang in langs:
        checks = list_checks(lang)
        all_checks[lang].append(checks)
        num_checks += len(checks)
    print("{} langs, {} checks supported".format(len(langs), num_checks))

    # TODO(bzz): debug log level
    print("Langs: ", langs)
    print("Checks: ", checks)

def main():
    print("starting gRPC Analyzer server at port {}".format(port_to_listen))
    print_check_stats()
    serve()

if __name__ == "__main__":
    main()