#!/bin/bash
VERSION=`grep version src/setup.py |awk -F = '{print $2}' |sed -r 's/( |,|\")//g'`
docker build -t galintools:latest -t galintools:${VERSION} .
