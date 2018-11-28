#!/usr/bin/env python3

# Analyzer that wrapps https://github.com/bblfsh/sonar-checks

from concurrent.futures import ThreadPoolExecutor

import os
import time
import grpc
import collections
import logging

from lookout.sdk import AnalyzerServicer, add_analyzer_to_server
from lookout.sdk import service_analyzer_pb2
from lookout.sdk import service_data_pb2_grpc
from lookout.sdk import service_data_pb2
from lookout.sdk.grpc import to_grpc_address, create_channel
from bblfsh_sonar_checks import run_checks, list_checks
from bblfsh_sonar_checks.utils import list_langs
from bblfsh import filter as filter_uast

version = "alpha"
host_to_bind = os.getenv('SONARCHECK_HOST', "0.0.0.0")
port_to_listen = os.getenv('SONARCHECK_PORT', 2022)
data_srv_addr = to_grpc_address(
    os.getenv('SONARCHECK_DATA_SERVICE_URL', "ipv4://localhost:10301"))
log_level = os.getenv('SONARCHECK_LOG_LEVEL', "info").upper()

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
logger.addHandler(handler)
logger.setLevel(log_level)


class Analyzer(AnalyzerServicer):
    def NotifyReviewEvent(self, request, context):
        logger.debug("got review request %s", request)

        # client connection to DataServe
        channel = create_channel(data_srv_addr)
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
            if not change.HasField("head"):
                continue

            logger.debug("analyzing '%s' in %s",
                         change.head.path, change.head.language)
            try:
                check_results = run_checks(
                    list_checks(change.head.language.lower()),
                    change.head.language.lower(),
                    change.head.uast
                )
            except Exception as e:
                logger.exception("Error during analyzing file '%s' in commit '%s': %s",
                                 change.head.path, request.commit_revision.head.hash, e)
            n = 0
            for check in check_results:
                for res in check_results[check]:
                    comments.append(
                        service_analyzer_pb2.Comment(
                            file=change.head.path,
                            line=res["pos"]["line"] if res and "pos" in res and res["pos"] and "line" in res["pos"] else 0,
                            text="{}: {}".format(check, res["msg"])))
                    n += 1
        logger.info("%d comments produced", n)
        return service_analyzer_pb2.EventResponse(analyzer_version=version, comments=comments)

    def NotifyPushEvent(self, request, context):
        pass


def serve():
    server = grpc.server(thread_pool=ThreadPoolExecutor(max_workers=10))
    add_analyzer_to_server(Analyzer(), server)
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
    logger.info("%d langs, %d checks supported", len(langs), num_checks)

    logger.debug("Langs: %s", langs)
    logger.debug("Checks: %s", checks)


def main():
    logger.info("starting gRPC Analyzer server at port %d", port_to_listen)
    print_check_stats()
    serve()


if __name__ == "__main__":
    main()
