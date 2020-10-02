#!/usr/bin/env bash

set -e
set -o pipefail

# required parameters
APPLICATION_TAG=${APPLICATION_TAG}
DEPLOY_TAG=${DEPLOY_TAG}
ACCESS=${AWS_ACCESS_KEY_ID}
KEY=${AWS_SECRET_ACCESS_KEY}

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
  echo "Tagging"
}

create_credentials(){

  echo -e "[auth] \n
      aws_access_key_id = ${ACCESS} \n
      aws_secret_access_key = ${KEY} \n
      " > aws/credentials
}

tag_instance(){
    export AWS_CONFIG_FILE=aws/config
    export AWS_SHARED_CREDENTIALS_FILE=aws/credentials

  i=$(aws ec2 describe-instances \
  --filters "Name=tag:Codedeploy,Values=Tesla" --profile ${PROFILE} --region ${REGION} --query "Reservations[*].Instances[*].[InstanceId]" --output text)

  b=$(aws ec2 describe-instances \
  --filters "Name=instance-state-code,Values=80" --instance-ids $i  --profile production --query "Reservations[*].Instances[*].[InstanceId]" --output text)

  # aws secretsmanager get-secret-value --secret-id ${SECRET} --query SecretString --output text --region ${REGION}  --profile ${PROFILE}
  # | jq -r 'to_entries|map("\(.key)=\(.value|tostring)")|.[]' > ${FILE} || { echo 'Failed' ; exit 1; }
}

completed(){
  echo "Tagged"
}

create_config
check_variables
start
create_credentials
tag_instance
completed
