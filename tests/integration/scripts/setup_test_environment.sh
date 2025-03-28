#!/bin/bash

docker run \
  --name pgsql-test \
  -e POSTGRES_USER=test \
  -e POSTGRES_PASSWORD=test  \
  -e POSTGRES_DB=test \
  -p 5433:5432 \
  -d postgres:16.0-alpine3.18


docker run \
  --name redis-test \
  --volume "./configs/:/usr/local/etc/redis" \
  -p 6380:6379 \
  -d redis:7.2.4-alpine

sleep 10