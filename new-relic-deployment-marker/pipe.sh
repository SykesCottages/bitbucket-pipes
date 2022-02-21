#!/bin/sh

set -e
set -o pipefail

## Required Parameters
NEW_RELIC_API_KEY=${NEW_RELIC_API_KEY}
NEW_RELIC_APPLICATION_ID=${NEW_RELIC_APPLICATION_ID}
DEPLOYMENT_REVISION=${DEPLOYMENT_REVISION}

## Optional Parameters
DEPLOYMENT_USER=${DEPLOYMENT_USER:='bitbucket.pipeline'}
NEW_RELIC_REGION=${NEW_RELIC_REGION:='US'}

if [ -z "$NEW_RELIC_APPLICATION_ID" ]; then
  echo "Missing Application ID"
  exit 1;
fi

OLD_IFS=$IFS
IFS=,
for APP in $NEW_RELIC_APPLICATION_ID; do
  newrelic apm deployment create \
    --applicationId "${APP}" \
    --user "${DEPLOYMENT_USER}" \
    --revision "${DEPLOYMENT_REVISION}"
done
IFS=$OLD_IFS

