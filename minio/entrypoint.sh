#!/bin/bash

minio server /data --console-address ":9090" &

while true; do
  response=$(curl -o /dev/null -s -w "%{http_code}\n" -u ${AWS_ACCESS_KEY_ID}:${AWS_SECRET_ACCESS_KEY} http://localhost:9090)
  if [ "$response" -eq 200 ]; then
    echo "Minio is up and running!"
    break
  else
    echo "Waiting for Minio to be ready... Received HTTP status: $response"
    sleep 1
  fi
done


ALIAS="local"
BUCKETS=("bronze" "silver" "gold")

mc alias set $ALIAS ${AWS_ENDPOINT} ${AWS_ACCESS_KEY_ID} ${AWS_SECRET_ACCESS_KEY}

for bucket_name in "${BUCKETS[@]}"; do
    # List all buckets and grep for your bucket
    bucket_exists=$(mc ls $ALIAS | grep $bucket_name)

    # If the bucket doesn't exist, create it
    if [ -z "$bucket_exists" ]; then
        echo "Bucket '$bucket_name' does not exist. Creating..."
        mc mb $ALIAS/$bucket_name
    else
        echo "Bucket '$bucket_name' already exists."
    fi
done

# Keep docker up
tail -f /dev/null