#!/usr/bin/env bash

set -e
set -o pipefail


# required parameters
APPLICATION_TAG=${APPLICATION_TAG}
APPLICATION_TAG_VALUE=${APPLICATION_TAG_VALUE}
DEPLOY_TAG=${DEPLOY_TAG}
DEPLOY_TAG_VALUE=${DEPLOY_TAG_VALUE}
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
  echo "Starting EC2 Instance Tagger"
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
      --filters "Name=tag:${APPLICATION_TAG},Values=${APPLICATION_TAG_VALUE}" --profile ${PROFILE} --region ${REGION} --query "Reservations[*].Instances[*].[InstanceId]" --output text)

    if [ -z "${i}" ]
    then
      echo "No instance tagged with the APPLICATION_TAG - ${APPLICATION_TAG}:${APPLICATION_TAG_VALUE}"
    else
      echo "Instances found '${i}' with APPLICATION_TAG - ${APPLICATION_TAG}:${APPLICATION_TAG_VALUE}"
        echo "Removing DEPLOY_TAG - ${DEPLOY_TAG}:${DEPLOY_TAG_VALUE} From instance:"${i}
        aws ec2 delete-tags \
          --resources ${i} \
          --tags "Key=${DEPLOY_TAG},Value=${DEPLOY_TAG_VALUE}" --profile ${PROFILE} 
        echo "Removed DEPLOY_TAG - ${DEPLOY_TAG}:${DEPLOY_TAG_VALUE} From instance:"${i}
    fi


    j=$(aws ec2 describe-instances \
      --filters "Name=tag:${APPLICATION_TAG},Values=${APPLICATION_TAG_VALUE}" --profile ${PROFILE} --region ${REGION} --query "Reservations[*].Instances[*].[InstanceId]" --output text)


    if [ -z "${j}" ]
    then
      echo "No instances with the APPLICATION_TAG - ${APPLICATION_TAG}:${APPLICATION_TAG_VALUE}"
    else
      echo "Instance found with the APPLICATION_TAG - ${APPLICATION_TAG}:${APPLICATION_TAG_VALUE}"
      c=$(aws ec2 describe-instances \
        --filters "Name=instance-state-name,Values=running" --instance-ids ${j}  --profile ${PROFILE} --region ${REGION} --query "Reservations[*].Instances[*].[InstanceId]" --output text)  
    fi


  if [ -z "${c}" ]
    then
      echo "No instances running with the APPLICATION_TAG - ${APPLICATION_TAG}:${APPLICATION_TAG_VALUE}"
    else
      echo "Running instance:${c} found with the APPLICATION_TAG - ${APPLICATION_TAG}:${APPLICATION_TAG_VALUE}"
      echo "Adding DEPLOY_TAG:${DEPLOY_TAG} to instance:"${c}
      aws ec2 create-tags \
        --resources ${c} --tags Key=${DEPLOY_TAG},Value=${DEPLOY_TAG_VALUE} --profile ${PROFILE} 
      echo "DEPLOY_TAG - ${DEPLOY_TAG}:${DEPLOY_TAG_VALUE} added to instance:"${c}
    fi


    # aws secretsmanager get-secret-value --secret-id ${SECRET} --query SecretString --output text --region ${REGION}  --profile ${PROFILE}
    # | jq -r 'to_entries|map("\(.key)=\(.value|tostring)")|.[]' > ${FILE} || { echo 'Failed' ; exit 1; }
}

completed(){
  echo "EC2 Instance Tagger Completed"
}

create_config
check_variables
start
create_credentials
tag_instance
completed

