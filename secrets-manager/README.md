# Bitbucket Secrets Manager

Access AWS Secrets Manager in Bitbucket pipeline.


## YAML Definition

Add the following snippet to the script section of your `bitbucket-pipelines.yml` file:

```yaml
  - pipe: sykescottages/bitbucket-pipes:secrets-manager-v2
    variables:
      FILE: '.env'
      AWS_ACCESS_KEY_ID: '<string>'
      AWS_SECRET_ACCESS_KEY: '<string>'
      AWS_OIDC_ROLE_ARN: $AWS_OIDC_ROLE_ARN
      AWS_DEFAULT_REGION: $AWS_DEFAULT_REGION
      AWS_SECRET_NAME: $AWS_SECRET_NAME
```

## Variables

| Variable                         | Usage                                              |
|----------------------------------|----------------------------------------------------|
| FILE                             | File Name you wish you save to. (defaults to .env) |
| AWS_ACCESS_KEY_ID (Optional)     | AWS Access Key Id.                                 |
| AWS_OIDC_ROLE_ARN (Optional)     | AWS OIDC Arn                                       |
| AWS_SECRET_ACCESS_KEY (Optional) | AWS Secret Key.                                    |
| AWS_SECRET_NAME (*)              | The name of the Secret Manager resource.           |
| AWS_DEFAULT_REGION (*)           | AWS Default Region.                                |

(*) = required variable. This variable needs to be specified always when using the pipe.
You must either pass in the OIDC Role Arn, or the AWS Access Key Id and Secret Key

## Prerequisites

To use this pipe you should have AWS Secrets Manager setup.
If using OIDC, the bitbucket pipelines step must declare the `oidc: true` parameter.

## Examples

Example pipe yaml

```yaml
    - step: &deploy
        image: node:latest
        oidc: true
        caches:
          - node
          - docker
        script:
          - pipe: docker://sykescottages/bitbucket-pipes:secrets-manager-v2
            variables:
              FILE: '.env'
              AWS_OIDC_ROLE_ARN: $AWS_OIDC_ROLE_ARN
              AWS_DEFAULT_REGION: $AWS_DEFAULT_REGION
              AWS_SECRET_NAME: $AWS_SECRET_NAME
          - ./deploy.sh
```

