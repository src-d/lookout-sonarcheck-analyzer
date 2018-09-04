# [![Build Status](https://travis-ci.org/src-d/lookout-sonarcheck-analyzer.svg)](https://travis-ci.org/src-d/lookout-sonarcheck-analyzer) lookout analyzer: sonarcheck

A [lookout](https://github.com/src-d/lookout/) analyzer implementation that uses bblfsh UAST and a [sonar-checks](https://github.com/bblfsh/sonar-checks).

_Disclamer: this is not official product, but only serves the purpose of testing the lookout._


# Example of utilization

With `lookout-sdk` binary from the latest release of [SDK](https://github.com/src-d/lookout/releases):

```
$ python3 lookout-sonarcheck.py

$ lookout-sdk review -v ipv4://localhost:2001 \
    --from c99dcdff172f1cb5505603a45d054998cb4dd606 \
    --to 3a9d78bdd1139c929903885ecb8f811931b8aa70
```


# Configuration

| Variable | Default | Description |
| -- | -- | -- |
| `SONARCHECK_HOST` | `0.0.0.0` | IP address to bind the gRCP serve |
| `SONARCHECK_PORT` | `2002` | Port to bind the gRPC server |
| `SONARCHECK_SERVER_URL` | `ipv4://localhost:10302` | gRPC URL of the [Data service](https://github.com/src-d/lookout/tree/master/docs#components)
| `SONARCHECK_LOG_LEVEL` | `info` | Logging level (info, debug, warning or error) |

# Development
## Release

Main release artifact is a Docker image, so
 
  - `make docker-push`


# Licens

AGPLv3
