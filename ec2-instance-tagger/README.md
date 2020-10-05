# Bitbucket EC2 Instance Tagger

Tag running AWS EC2 Instance ready for deployment in Bitbucket pipeline.

## YAML Definition

Add the following snippet to the script section of your `bitbucket-pipelines.yml` file:

```yaml
- pipe: sykescottages/bitbucket-secrets-manager
    APPLICATION_TAG: '<string>'
    APPLICATION_TAG_VALUE: '<string>'
    DEPLOY_TAG: '<string>'
    DEPLOY_TAG_VALUE: '<string>'
    AWS_ACCESS_KEY_ID: '<string>'
    AWS_SECRET_ACCESS_KEY: '<string>'
    AWS_REGION: '<string>'
    AWS_PROFILE: '<string>'
    CONFIG: '<string>'  
```

## Variables

| Variable              | Usage                                                       |
| --------------------- | ----------------------------------------------------------- |
| APPLICATION_TAG (*)| Name of the EC2 target tag |
| APPLICATION_TAG_VALUE (*)| Value of the EC2 target tag |
| DEPLOY_TAG  (*)| Name of the EC2 deploy tag |
| DEPLOY_TAG_VALUE  (*)| Value of the EC2 deploy tag |
| AWS_ACCESS_KEY_ID (*) | AWS key id. |
| AWS_SECRET_ACCESS_KEY (*) | AWS secret key. |
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
  - pipe: sykescottages/bitbucket-ec2-instance-tagger
    variables:
      APPLICATION_TAG: 'Application'
      APPLICATION_TAG_VALUE: 'Example'
      DEPLOY_TAG: 'Codedeploy'
      DEPLOY_TAG_VALUE: 'Ready'
      AWS_ACCESS_KEY_ID: $AWS_ACCESS_KEY
      AWS_SECRET_ACCESS_KEY: $AWS_SECRET_KEY
      AWS_REGION: eu-west-1
      AWS_PROFILE: staging
```

