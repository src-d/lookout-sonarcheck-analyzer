# [![Build Status](https://travis-ci.org/src-d/lookout-sonarcheck-analyzer.svg)](https://travis-ci.org/src-d/lookout-sonarcheck-analyzer) lookout analyzer: sonarcheck

A [lookout](https://github.com/src-d/lookout/) analyzer implementation that uses bblfsh UAST and [sonar-checks](https://github.com/bblfsh/sonar-checks).

_Disclaimer: this is not an official product, it only serves the purpose of testing lookout._


# Example of utilization

Install **lookout-sonarcheck** dependencies running:

```shell
$ pip3 install -r requirements.txt
```

Run **lookout-sonarcheck** analyzer

```shell
$ python3 sonarcheck_analyzer.py
```

With `lookout-sdk` binary from the latest release of [SDK](https://github.com/src-d/lookout/releases), run:

```shell

$ lookout-sdk review --log-level=debug \
    --from c99dcdff172f1cb5505603a45d054998cb4dd606 \
    --to 3a9d78bdd1139c929903885ecb8f811931b8aa70
```


# Configuration

| Variable | Default | Description |
| -- | -- | -- |
| `SONARCHECK_HOST` | `0.0.0.0` | IP address to bind the gRPC serve |
| `SONARCHECK_PORT` | `9930` | Port to bind the gRPC server |
| `SONARCHECK_DATA_SERVICE_URL` | `ipv4://localhost:10301` | gRPC URL of the [Data service](https://github.com/src-d/lookout/tree/master/docs#components)
| `SONARCHECK_LOG_LEVEL` | `info` | Logging level (info, debug, warning or error) |

# Development
## Release

Main release artifact is a Docker image, so
 
  - `make docker-push`


# License

[AGPLv3](./LICENSE)
