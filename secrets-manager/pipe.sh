#!/usr/bin/env bash

set -e
set -o pipefail

# required parameters
FILE=${FILE:=.env}
ACCESS=${AWS_ACCESS_KEY_ID}
KEY=${AWS_SECRET_ACCESS_KEY}
SECRET=${AWS_SECRET_NAME}
REGION=${AWS_REGION}
PROFILE=${AWS_PROFILE}
CONFIG=${CONFIG:='https://s3-auth-ew1-bitbucket-secrets-manager-bucket-config.s3-eu-west-1.amazonaws.com/config'}
DEBUG=${DEBUG:=false}


create_config(){
  mkdir aws
  curl "${CONFIG}" > aws/config
}

check_variables(){

  if [ ! -e aws/config ]; then
    echo "Cant not access the AWS Config file."
    exit 1
  fi

  if ! [ -n "${ACCESS}" ]; then
    echo "Set the AWS access key."
    exit 1
  fi

  if ! [ -n "${KEY}" ]; then
    echo "Set the AWS Secret key."
    exit 1
  fi

  if ! [ -n "${SECRET}" ]; then
    echo "Provid The name of the AWS secrest"
    exit 1
  fi

  if ! [ -n "${REGION}" ]; then
    echo "Provid the AWS Region"
    exit 1
  fi

  if ! [ -n "${PROFILE}" ]; then
    echo "Provid the AWS IAM profile"
    exit 1
  fi

}

start(){
  echo "Getting Secret"
}

create_credentials(){

  echo -e "[auth] \n
      aws_access_key_id = ${ACCESS} \n
      aws_secret_access_key = ${KEY} \n
      " > aws/credentials
}

get_secrets(){
    export AWS_CONFIG_FILE=aws/config
    export AWS_SHARED_CREDENTIALS_FILE=aws/credentials

  aws secretsmanager get-secret-value --secret-id ${SECRET} --query SecretString --output text --region ${REGION}  --profile ${PROFILE} | jq -r 'to_entries|map("\(.key)=\(.value|tostring)")|.[]' > ${FILE} || { echo 'Failed' ; exit 1; }
}

completed(){

  if [ -f "${FILE}" ]; then

    if [ ${DEBUG} = true ]; then
      echo "I Hope you know what you are doing."

      cat ${FILE}

      echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
      echo "Please delete the pipeline logs."
      echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    fi

  else
    echo "Error"
  fi
}

create_config
check_variables
start
create_credentials
get_secrets
completed
