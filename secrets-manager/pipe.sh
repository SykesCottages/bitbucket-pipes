#!/usr/bin/env bash
#
# Get values from Secret Manager
#
# Required globals:
#   AWS_DEFAULT_REGION
#   AWS_SECRET_NAME
#   FILE

source "$(dirname "$0")/common.sh"

# mandatory parameters
AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION:?'AWS_DEFAULT_REGION variable missing.'}
AWS_SECRET_NAME=${AWS_SECRET_NAME:?'AWS_SECRET_NAME variable missing.'}
FILE=${FILE:-.env}


default_authentication() {
  info "Using default authentication with AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY."
  AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID:?'AWS_ACCESS_KEY_ID variable missing.'}
  AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY:?'AWS_SECRET_ACCESS_KEY variable missing.'}
}

oidc_authentication() {
  info "Authenticating with a OpenID Connect (OIDC) Web Identity Provider."
      mkdir -p /.aws-oidc
      AWS_WEB_IDENTITY_TOKEN_FILE=/.aws-oidc/web_identity_token
      echo "${BITBUCKET_STEP_OIDC_TOKEN}" >> ${AWS_WEB_IDENTITY_TOKEN_FILE}
      chmod 400 ${AWS_WEB_IDENTITY_TOKEN_FILE}
      aws configure set web_identity_token_file ${AWS_WEB_IDENTITY_TOKEN_FILE}
      aws configure set role_arn ${AWS_OIDC_ROLE_ARN}
      unset AWS_ACCESS_KEY_ID
      unset AWS_SECRET_ACCESS_KEY
}

setup_authentication() {
  enable_debug
  AWS_DEFAULT_REGION=${AWS_DEFAULT_REGION:?'AWS_DEFAULT_REGION variable missing.'}
  if [[ -n "${AWS_OIDC_ROLE_ARN}" ]]; then
    if [[ -n "${BITBUCKET_STEP_OIDC_TOKEN}" ]]; then
      oidc_authentication
    else
      warning 'Parameter `oidc: true` in the step configuration is required for OIDC authentication'
      default_authentication
    fi
  else
    default_authentication
  fi
}

setup_authentication

info "Getting values from Secret Manager..."
# Pipe standard output to /dev/null so run does not echo out secrets
run aws secretsmanager get-secret-value --region ${AWS_DEFAULT_REGION} --secret-id ${AWS_SECRET_NAME} --query SecretString --output text 1> /dev/null

if [[ "${status}" -eq 0 ]]; then
  # Create a new .env file (overwrite any existing one)
  > ${FILE:-.env}
  
  # Process each key-value pair from JSON without single quotes
  cat ${output_file} | jq -r 'to_entries[] | "\(.key)=\(.value)"' >> ${FILE:-.env}

  success "Exporting Secret Manager values to ${FILE} successful."
else
  fail "Getting Secret Manager values failed."
fi






