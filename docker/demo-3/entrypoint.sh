#!/bin/sh

function terminate {
  echo "terminating"
  exit 0
}

trap terminate SIGTERM SIGINT

while true; do echo -e "HTTP/1.1 200 OK\n\nHello from nc" | nc -l -p 1234 -v; done &

wait
