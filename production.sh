#!/bin/bash

# GET CREDENTIALS
echo "get credentials"
for env in $(curl 169.254.170.2$AWS_CONTAINER_CREDENTIALS_RELATIVE_URI | jq '. | {AWS_ACCESS_KEY_ID: .AccessKeyId, AWS_SECRET_ACCESS_KEY: .SecretAccessKey, AWS_SESSION_TOKEN: .Token  }' | jq -r "to_entries|map(\"\(.key)=\(.value|tostring)\")|.[]"); do
  export $env
done

# RUN APPLCIATION
python mba.py run
EXIT_CODE=$?