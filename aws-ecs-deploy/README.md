# Bitbucket Secrets Manager

Deploy to AWS ECS using Bitbucket pipeline with AWS role support.

## YAML Definition

Add the following snippet to the script section of your `bitbucket-pipelines.yml` file:

```yaml
- pipe: sykescottages/bitbucket-secrets-manager
    AWS_ACCESS_KEY_ID: '<string>'
    AWS_SECRET_ACCESS_KEY: '<string>'
    AWS_ECS_SERVICE_NAME: '<string>'
    AWS_ECS_CLUSTER_NAME: '<string>'
    AWS_ECR_ACCOUNT_ID: '<string>'
    AWS_ECR_IMAGE_NAME: '<string>'
    AWS_REGION: '<string>'
    AWS_PROFILE: '<string>'
    CONFIG: '<string>'  
```

## Variables

| Variable              | Usage                                                       |
| --------------------- | ----------------------------------------------------------- |
| AWS_ACCESS_KEY_ID (*)              | AWS key id. |
| AWS_SECRET_ACCESS_KEY (*) | AWS secret key. |
| AWS_ECS_SERVICE_NAME (*) | ECS service name |
| AWS_ECS_CLUSTER_NAME (*) | ECS cluster name |
| AWS_ECR_ACCOUNT_ID | AWS account ID |
| AWS_ECR_IMAGE_NAME (*) | Docker image name |
| AWS_REGION (*) | AWS region. |
| AWS_PROFILE (*) | The name of the AWS profile. eg default, production, non-prod, staging, dev |
| CONFIG               | Path to AWS config file eg (s3 restricted access) |
_(*) = required variable. This variable needs to be specified always when using the pipe._

#### Workspaces Variables
- $AWS_ACCESS_KEY
- $AWS_SECRET_KEY

## Examples

Example pipe yaml

```yaml
script:
  - pipe: sykescottages/bitbucket-secrets-manager
    variables:
      AWS_ACCESS_KEY_ID: $AWS_ACCESS_KEY
      AWS_SECRET_ACCESS_KEY: $AWS_SECRET_KEY
      AWS_ECS_SERVICE_NAME: sm-s-ew1-project
      AWS_ECS_CLUSTER_NAME: service-f-e-ew1-example
      AWS_ECR_ACCOUNT_ID: "03023033203"
      AWS_ECR_IMAGE_NAME: "ecr-s-ew1-example-web"
      AWS_REGION: eu-west-1
      AWS_PROFILE: staging
```

