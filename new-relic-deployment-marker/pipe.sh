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

newrelic apm deployment create \
  --applicationId "${NEW_RELIC_APPLICATION_ID}" \
  --user "${DEPLOYMENT_USER}" \
  --revision "${DEPLOYMENT_REVISION}"
