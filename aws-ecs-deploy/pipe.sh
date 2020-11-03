#!/usr/bin/env bash

set -e
set -o pipefail

# required parameters
ACCESS=${AWS_ACCESS_KEY_ID}
KEY=${AWS_SECRET_ACCESS_KEY}
REGION=${AWS_REGION}
PROFILE=${AWS_PROFILE}
SERVICE=${AWS_ECS_SERVICE_NAME}
CLUSTER=${AWS_ECS_CLUSTER_NAME}
ACCOUNT=${AWS_ECR_ACCOUNT_ID}
IMAGE=${AWS_ECR_IMAGE_NAME}

CONFIG=${CONFIG:='https://s3-auth-ew1-bitbucket-secrets-manager-bucket-config.s3-eu-west-1.amazonaws.com/config'}

OK=$(echo "[OK] - ")
ERROR=$(echo "[ERROR] - ")
INFO=$(echo "[INFO] - ")
TIMEOUT=300
AWS="aws --profile $PROFILE --region $REGION"

create_config(){
  mkdir -p aws
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

  if ! [ -n "${SERVICE}" ]; then
    echo "Provid The name of the service"
    exit 1
  fi

  if ! [ -n "${CLUSTER}" ]; then
    echo "Provid The name of the cluster"
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

  if ! [ -n "${ACCOUNT}" ]; then
    echo "Provid the AWS account ID"
    exit 1
  fi

  if ! [ -n "${IMAGE}" ]; then
    echo "Provid the AWS ECR image name"
    exit 1
  fi


}

start(){
  echo "Starting Deployment"
}

create_credentials(){

  echo -e "[auth] \n
      aws_access_key_id = ${ACCESS} \n
      aws_secret_access_key = ${KEY} \n
      " > aws/credentials
}

ecs_deploy(){
    export AWS_CONFIG_FILE=aws/config
    export AWS_SHARED_CREDENTIALS_FILE=aws/credentials
    AWS_ECR_URL="dkr.ecr.eu-west-1.amazonaws.com"
    # Replace the container name in the task definition with the new image.
    export IMAGE_NAME="${AWS_ECR_ACCOUNT_ID}.${AWS_ECR_URL}/${AWS_ECR_IMAGE_NAME}:${BITBUCKET_BUILD_NUMBER}"

    envsubst < task-definition.json >  task-definition-envsubst.json
    # Update the task definition and capture the latest revision.
    export UPDATED_TASK_DEFINITION=$($AWS ecs register-task-definition --cli-input-json file://task-definition-envsubst.json | \
    jq '.taskDefinition.taskDefinitionArn' --raw-output)
    
    $AWS ecs update-service --service ${SERVICE} --cluster ${CLUSTER} --output table --task-definition ${UPDATED_TASK_DEFINITION} || { echo 'Failed' ; exit 1; }
}

waitForDeploy(){
  DEPLOYMENT_SUCCESS="false"
  every=2
  i=0
  echo "Waiting for service deployment to complete..."
  while [ $i -lt $TIMEOUT ]
  do
    NUM_DEPLOYMENTS=$($AWS ecs describe-services --cluster ${CLUSTER} --service ${SERVICE}| jq "[.services[].deployments[]] | length")
    # Wait to see if more than 1 deployment stays running
    # If the wait time has passed, we need to roll back
    if [ $NUM_DEPLOYMENTS -eq 1 ]; then
      echo -e "${OK} Service deployment successful. Time = ${i} seconds"
      DEPLOYMENT_SUCCESS="true"
      # Exit the loop.
      i=$TIMEOUT
    else
      sleep $every
      i=$(( $i + $every ))
    fi
  done
  if [[ "${DEPLOYMENT_SUCCESS}" != "true" ]]; then
    echo -e "${ERROR} failed to deploy."
    exit 1
  fi
}

create_config
check_variables
start
create_credentials
ecs_deploy
waitForDeploy
