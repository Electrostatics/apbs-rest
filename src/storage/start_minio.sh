#!/bin/bash
MINIO_ACCESS_KEY=admin
MINIO_SECRET_KEY=adminadmin
docker run --rm -it -p 9000:9000 \
    -e MINIO_ACCESS_KEY=$MINIO_ACCESS_KEY\
    -e MINIO_SECRET_KEY=$MINIO_SECRET_KEY\
    minio/minio server /data