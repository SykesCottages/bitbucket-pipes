# Bitbucket Secrets Manager

Access AWS secrets manager in Bitbucket pipeline.

## YAML Definition

Add the following snippet to the script section of your `bitbucket-pipelines.yml` file:

```yaml
- pipe: sykescottages/bitbucket-secrets-manager
    FILE: '<string>'
    AWS_ACCESS_KEY_ID: '<string>'
    AWS_ACCESS_KEY_ID: '<string>'
    AWS_SECRET_ACCESS_KEY: '<string>'
    AWS_SECRET_NAME: '<string>'
    AWS_REGION: '<string>'
    AWS_PROFILE: '<string>'
    CONFIG: '<string>'  
```

## Variables

| Variable              | Usage                                                       |
| --------------------- | ----------------------------------------------------------- |
| FILE             | File Name you Wish you save to. (Default .env)|
| AWS_ACCESS_KEY_ID (*)              | AWS key id. |
| AWS_SECRET_ACCESS_KEY (*) | AWS secret key. |
| AWS_SECRET_NAME (*) | The name of the secret. |
| AWS_REGION (*) | AWS region. |
| AWS_PROFILE (*) | The name of the AWS profile. eg default, production, non-prod, staging, dev |
| CONFIG               | Path to AWS config file eg (s3 restricted access) |
_(*) = required variable. This variable needs to be specified always when using the pipe._

#### Workspaces Variables
- $AWS_ACCESS_KEY
- $AWS_SECRET_KEY

## Prerequisites

To use this pipe you should have AWS secrets manager setup.

## Examples

Example pipe yaml

```yaml
script:
  - pipe: sykescottages/bitbucket-secrets-manager
    variables:
      AWS_ACCESS_KEY_ID: $AWS_ACCESS_KEY
      AWS_SECRET_ACCESS_KEY: $AWS_SECRET_KEY
      AWS_SECRET_NAME: sm-s-ew1-project
      AWS_REGION: eu-west-1
      AWS_PROFILE: staging
```

