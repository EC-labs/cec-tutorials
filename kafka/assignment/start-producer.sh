#!/bin/bash


script=$(basename "$0")

USAGE="
Usage: $script <auth> <topic> <brokers> [OPTIONS] 

Positional parameters:
    auth: path to authentication directory with credentials. E.g. /home/ubuntu/cec-tutorials/kafka/auth
    topic: The topic where messages are to be produced.
    brokers: The kafka broker <ip>:<port> connection. E.g. 13.60.146.188:19093

Options:
      --secret-key <secret-key>
          <key> is a 32 character string that must match the key being passed to the notifications-service [default: QJUHsPhnA0eiqHuJqsPgzhDozYO4f1zh]
      --config-file <config-file>
      --num-sensors <num-sensors>
          [default: 2]
      --sample-rate <sample-rate>
          [default: 100]
      --stabilization-samples <stabilization-samples>
          [default: 2]
      --carry-out-samples <carry-out-samples>
          [default: 20]
      --start-temperature <start-temperature>
          [default: 16]
      --lower-threshold <lower-threshold>
          [default: 25.5]
      --upper-threshold <upper-threshold>
          [default: 26.5]
      --topic-document <topic-document>

      --file-subscriber
          Whether a tracing subscriber should be created to persist the experiment-producer logs
      --no-ssl
          Producer connects with broker with SSL protocol
  -h, --help
          Print help
  -V, --version
          Print version
"

if (( $# < 3 )); then
    echo "$USAGE"
    exit 1
fi

auth="$1"; shift
topic="$1"; shift
brokers="$1"; shift

if ! [[ -d "$auth" ]]; then
    echo "'$auth' is not a directory. It should be a credentials directory"
    exit 1
fi

docker run \
    --rm \
    -v "$(realpath $auth)":/app/experiment-producer/auth \
    dclandau/cec-experiment-producer \
    --topic "$topic" --brokers "$brokers" "$@"
