#!/usr/bin/env bash

set -e
set -o pipefail

# required parameters
ACCESS=${AWS_ACCESS_KEY_ID}
KEY=${AWS_SECRET_ACCESS_KEY}
ACCOUNT=${AWS_ECR_ACCOUNT_ID}
IMAGE=${IMAGE_NAME}
REGION=${AWS_REGION}
PROFILE=${AWS_PROFILE}
CONFIG=${CONFIG:='https://s3-auth-ew1-bitbucket-secrets-manager-bucket-config.s3-eu-west-1.amazonaws.com/config'}


create_config(){
  mkdir -p aws

  if [ ! -f "aws/config" ]; then
    curl "${CONFIG}" > aws/config
  else
    echo 'AWS Config already exists' >&2
  fi

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

  if ! [ -n "${IMAGE}" ]; then
    echo "Provid the AWS ECR image name"
    exit 1
  fi

  if ! [ -n "${ACCOUNT}" ]; then
    echo "Provid The name of the AWS ECR Account ID"
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
  echo "Starting AWS ECR Pipe"
}

create_credentials(){

  if [ ! -f "aws/credentials" ]; then
    echo -e "[auth] \n
      aws_access_key_id = ${ACCESS} \n
      aws_secret_access_key = ${KEY} \n
      " > aws/credentials
  else
    echo 'AWS Credentials already exists' >&2
  fi
  
}

dockerLogin(){

  export AWS_CONFIG_FILE=aws/config
  export AWS_SHARED_CREDENTIALS_FILE=aws/credentials
  export AWS="aws --profile $PROFILE --region $REGION"
  $AWS ecr get-login-password | docker login --username AWS --password-stdin ${ACCOUNT}.dkr.ecr."${REGION}".amazonaws.com > /dev/null

  if [ "$?" != "0" ];then
    echo "[ERROR] - Login to registry failed."
  else
    echo "[INFO] - Logged on to registry."
  fi
}

pushImages(){
  docker images
  IMAGES=$(docker images | grep -i ${BITBUCKET_BUILD_NUMBER})
  AWS_ECR_URL="dkr.ecr.eu-west-1.amazonaws.com"
  export FULL_IMAGE_NAME="${ACCOUNT}.${AWS_ECR_URL}/${IMAGE}"
  if [ -z "$IMAGES" ];then
    echo "[INFO] - IMAGE_ID is empty"
    exit 2
  else
    echo "[INFO] - Preparing to publish image..."
    # docker-compose -f $DOCKER_COMPOSE_FILE push
    echo "[INFO] - Tagging image latest ..."
    docker tag ${IMAGE_NAME} ${FULL_IMAGE_NAME}:${BITBUCKET_BUILD_NUMBER}
    docker push ${FULL_IMAGE_NAME}:${BITBUCKET_BUILD_NUMBER}
  fi
}


cleaup_credentials(){
  echo "Tidying up after Pipe"
  rm -r aws
}

create_config
check_variables
start
create_credentials
dockerLogin
pushImages
cleaup_credentials