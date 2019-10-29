#!/bin/bash

MINIO_ACCESS_KEY=admin
MINIO_SECRET_KEY=adminadmin

if [ "$1" != "" ]
then
    echo "Port declared: $1"
    PORT="$1"
else
    echo "No port specified. Default: 9000"
    PORT="9000"
fi

docker run --rm -it -p $PORT:9000 \
    -e MINIO_ACCESS_KEY=$MINIO_ACCESS_KEY\
    -e MINIO_SECRET_KEY=$MINIO_SECRET_KEY\
    minio/minio server /data