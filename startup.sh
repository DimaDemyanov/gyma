#!/usr/bin/env bash

set -e

python3 ./server.py --profile $PROFILE 
# >/tmp/logs/mrs_$BUILD_NUMBER.log 2>/tmp/logs/mrs_$BUILD_NUMBER.log
