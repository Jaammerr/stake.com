#!/bin/bash
# wait-for-it.sh
# Usage: ./wait-for-it.sh host:port -- command args

set -e

host="$1"
port="$2"
shift 2
# shellcheck disable=SC2124
cmd="$@"

until nc -z "$host" "$port"; do
  >&2 echo "Waiting for $host:$port..."
  sleep 1
done

>&2 echo "$host:$port is available"
exec $cmd