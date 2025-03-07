# Bitbucket Pipe: Terragrunt config export

This pipe retrieves all the config needed to pass into a helm chart to deploy the sandbox environments.
## YAML Definition

Add the following to your `bitbucket-pipelines.yml` file:

```yaml
- pipe: 
  variables:
    ECS_CLUSTER: 'my-ecs-cluster'
    ECS_SERVICE: 'my-ecs-service'
    AWS_OIDC_ROLE_ARN: 'arn:aws:iam::account-id:role/role-name'
    MAIN_CONTAINER_NAME: 'web'
    # Optional variables
    EXTRA_ENV:'{"BASE_URL": "example.com"}' #Extra env vars to include in the config
    ENDPOINTS: '["authenticate"]'
    EXTERNAL_ENDPOINTS: ['authenticate']
    IAM_ROLE: 'arn:aws:iam::account-id:role/role-name'
    AWS_PROFILE: 'staging' 
    OUTPUT_FILE: 'values.yml' 
    AWS_REGION: 'eu-west-1'
```

## Variables

| Variable | Usage                                      | Required |
| -------- |--------------------------------------------| -------- |
| ECS_CLUSTER | Name of the ECS cluster                    | Yes |
| ECS_SERVICE | Name of the ECS service                    | Yes |
| AWS_OIDC_ROLE_ARN | OIDC Role to assume                        | Yes |
| MAIN_CONTAINER_NAME | The name of the main container for routing | Yes |
| EXTRA_ENV | Extra environment vars for the sevice      | No |
| ENDPOINTS | Endpoints for the target groups            | No |
| IAM_ROLE | IAM role for the service to use            | No |
| AWS_PROFILE | Profile to use to get the config           | No |
| OUTPUT_FILE | File to write the config to                | No |
| AWS_REGION | AWS region                                 | No |

## Examples

### Basic Usage

```yaml
- pipe: sykescottages/bitbucket-pipes:terragrunt-config-export
  variables:
    ECS_CLUSTER: 'my-ecs-cluster'
    ECS_SERVICE: 'my-ecs-service'
    AWS_OIDC_ROLE_ARN: 'arn:aws:iam::account-id:role/role-name'
```

### Write output to a file and use in subsequent steps

```yaml
- step:
    name: Extract ECS Configuration
    script:
      - pipe: sykescottages/bitbucket-pipes:terragrunt-config-export
        variables:
          ECS_CLUSTER: 'my-ecs-cluster'
          ECS_SERVICE: 'my-ecs-service'
          AWS_OIDC_ROLE_ARN: 'arn:aws:iam::account-id:role/role-name'
          MAIN_CONTAINER_NAME: "web"
          OUTPUT_FILE: 'values.yml'
      - cat values.yml
```

## Development

To build and test this pipe locally:

1. Build the Docker image:
   ```bash
   docker build -t terragrunt-config-export .
   ```

2. Run the pipe locally:
   ```bash
   docker run \
     -v ~/.aws:/root/.aws \
     -e ECS_CLUSTER="ew1-s-hyperion" \
     -e ECS_SERVICE="ew1-s-hyperion-webapp" \
     -e AWS_PROFILE=staging \
     -e ENDPOINTS='["authenticate"]' \
     -e EXTERNAL_ENDPOINTS='["authenticate"]' \
     -e EXTRA_ENV='{"BASE_URL": "example.com"}' \
     -e IAM_ROLE="arn:aws:iam::account-id:role/role-name" \
     -e MAIN_CONTAINER_NAME="web" \
      terragrunt-config-export
   ```