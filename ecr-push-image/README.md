# ECR Push Image

Push Docker Image to AWS ECR using Bitbucket pipeline with AWS role support.

## YAML Definition

Add the following snippet to the script section of your `bitbucket-pipelines.yml` file:

```yaml
- pipe: sykescottages/ecr-push-image
    AWS_ACCESS_KEY_ID: '<string>'
    AWS_ACCESS_KEY_ID: '<string>'
    AWS_ECR_ACCOUNT_ID: '<string>'
    IMAGE_NAME: '<string>'
    AWS_REGION: '<string>'
    AWS_PROFILE: '<string>'
    CONFIG: '<string>'  
```

## Variables

| Variable              | Usage                                                       |
| --------------------- | ----------------------------------------------------------- |
| AWS_ACCESS_KEY_ID (*)              | AWS key id. |
| AWS_SECRET_ACCESS_KEY (*) | AWS secret key. |
| AWS_ECR_ACCOUNT_ID | AWS account ID |
| IMAGE_NAME (*) | Docker image name |
| AWS_REGION (*) | AWS region. |
| AWS_PROFILE (*) | The name of the AWS profile. eg default, production, non-prod, staging, dev |
| CONFIG               | Path to AWS config file eg (s3 restricted access) |
_(*) = required variable. This variable needs to be specified always when using the pipe._

#### Workspaces Variables
- $AWS_ACCESS_KEY
- $AWS_SECRET_KEY

## Prerequisites

To use this pipe you should have AWS ECR setup

## Examples

Example pipe yaml

```yaml
script:
  - pipe: sykescottages/ecr-push-image
    variables:
      AWS_ACCESS_KEY_ID: $AWS_ACCESS_KEY
      AWS_SECRET_ACCESS_KEY: $AWS_SECRET_KEY
      AWS_ECR_ACCOUNT_ID: 0232342342379
      AWS_REGION: eu-west-1
      AWS_PROFILE: staging
      IMAGE_NAME: ecr-s-ew1-example-web
```

