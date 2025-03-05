# Bitbucket Pipe: Terragrunt config export

This pipe retrieves all the config needed to pass into a helm chart to deploy the sandbox environments.
## YAML Definition

Add the following to your `bitbucket-pipelines.yml` file:

```yaml
- pipe: 
  variables:
    ECS_CLUSTER: 'my-ecs-cluster'
    ECS_SERVICE: 'my-ecs-service'
<<<<<<< HEAD
    AWS_OIDC_ROLE_ARN: 'arn:aws:iam::account-id:role/role-name'
=======
>>>>>>> a0a9114ad1ee0534dd9c29b6381c0891977cb5b6
    # Optional variables
    EXTRA_ENV: #Extra env vars to include in the config
       BASE_URL: example.com
    ENDPOINTS: ['authenticate']
    IAM_ROLE: 'arn:aws:iam::account-id:role/role-name'
<<<<<<< HEAD
=======
    AWS_ROLE_ARN: 'arn:aws:iam::account-id:role/role-name'
>>>>>>> a0a9114ad1ee0534dd9c29b6381c0891977cb5b6
    AWS_PROFILE: 'staging' 
    OUTPUT_FILE: 'values.yml' 
    AWS_REGION: 'eu-west-1'
```

## Variables

<<<<<<< HEAD
| Variable | Usage                                 | Required |
| -------- |---------------------------------------| -------- |
| ECS_CLUSTER | Name of the ECS cluster               | Yes |
| ECS_SERVICE | Name of the ECS service               | Yes |
| AWS_OIDC_ROLE_ARN | OIDC Role to assume                   | Yes |
| EXTRA_ENV | Extra environment vars for the sevice | No |
| ENDPOINTS | Endpoints for the target groups       | No |
| IAM_ROLE | IAM role for the service to use       | No |
| AWS_PROFILE | Profile to use to get the config      | No |
| OUTPUT_FILE | File to write the config to           | No |
| AWS_REGION | AWS region                            | No |
=======
| Variable | Usage                                       | Required |
| -------- |---------------------------------------------| -------- |
| ECS_CLUSTER | Name of the ECS cluster                     | Yes |
| ECS_SERVICE | Name of the ECS service                     | Yes |
| EXTRA_ENV | Extra environment vars for the sevice       | No |
| ENDPOINTS | Endpoints for the target groups             | No |
| IAM_ROLE | IAM role for the service to use             | No |
| AWS_ROLE_ARN | ARN of IAM role to assume to get the config | No |
| AWS_PROFILE | Profile to use to get the config            | No |
| OUTPUT_FILE | File to write the config to                 | No |
| AWS_REGION | AWS region                                  | No |
>>>>>>> a0a9114ad1ee0534dd9c29b6381c0891977cb5b6

## Examples

### Basic Usage

```yaml
- pipe: your-docker-registry/ecs-container-definitions-pipe:latest
  variables:
    ECS_CLUSTER: 'my-ecs-cluster'
    ECS_SERVICE: 'my-ecs-service'
<<<<<<< HEAD
    AWS_OIDC_ROLE_ARN: 'arn:aws:iam::account-id:role/role-name'
=======
    AWS_ROLE_ARN: 'arn:aws:iam::account-id:role/role-name'
>>>>>>> a0a9114ad1ee0534dd9c29b6381c0891977cb5b6
```

### Write output to a file and use in subsequent steps

```yaml
- step:
    name: Extract ECS Configuration
    script:
      - pipe: your-docker-registry/ecs-container-definitions-pipe:latest
        variables:
          ECS_CLUSTER: 'my-ecs-cluster'
          ECS_SERVICE: 'my-ecs-service'
<<<<<<< HEAD
          AWS_OIDC_ROLE_ARN: 'arn:aws:iam::account-id:role/role-name'
=======
          AWS_ROLE_ARN: 'arn:aws:iam::account-id:role/role-name'
>>>>>>> a0a9114ad1ee0534dd9c29b6381c0891977cb5b6
          OUTPUT_FILE: 'values.yml'
      - cat values.yml.json
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
     -e AWS_PROFILE="staging" \
     terragrunt-config-export
   ```