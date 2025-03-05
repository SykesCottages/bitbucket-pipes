#!/usr/bin/env python3

import os
import sys
import boto3
import yaml
import time
import stat
import configparser


def auth_oidc():
    random_number = str(time.time_ns())
    aws_config_directory = os.path.join(os.environ["HOME"], '.aws')
    oidc_token_directory = os.path.join(aws_config_directory, '.aws-oidc')

    os.makedirs(aws_config_directory, exist_ok=True)
    os.makedirs(oidc_token_directory, exist_ok=True)

    web_identity_token_path = os.path.join(oidc_token_directory, f'oidc_token_{random_number}')
    with open(web_identity_token_path, 'w') as f:
        f.write(os.getenv('BITBUCKET_STEP_OIDC_TOKEN'))

    os.chmod(web_identity_token_path, mode=stat.S_IRUSR)
    print('Web identity token file is created')

    aws_configfile_path = os.path.join(aws_config_directory, 'config')
    with open(aws_configfile_path, 'w') as configfile:
        config = configparser.ConfigParser()
        config['default'] = {
            'role_arn': os.getenv('AWS_OIDC_ROLE_ARN'),
            'web_identity_token_file': web_identity_token_path
        }
        config.write(configfile)
    print('Configured settings for authentication with assume web identity role')

def get_boto3_client(service_name='ecs'):
    """
    Create and return a boto3 client with appropriate authentication.
    """
    region = os.getenv('AWS_REGION', os.getenv('AWS_DEFAULT_REGION', 'eu-west-1'))
    profile_name = os.getenv('AWS_PROFILE')
    oidc = os.getenv('AWS_OIDC_ROLE_ARN')

    if oidc:
        auth_oidc()
        return boto3.client(service_name,region_name=region)
    elif profile_name:
        session = boto3.Session(profile_name=profile_name)
        return session.client(service_name, region_name=region)

def convert_to_terragrunt_format(task_definition, service_name):
    """
    Convert ECS task definition to the required Terragrunt format.
    """
    # Initialize the terragrunt config structure
    config = {
        "deployment": {
            "extraEnv": os.getenv('EXTRA_ENV', [])
        },
        "terragruntConfig": {
            "name": f"({service_name})",
            "secrets": [],
            "containers": [],
            "mainContainerName": "",
            "resources": [],
            "endpoints": os.getenv('ENDPOINTS', []),
            "iamRole": os.getenv('IAM_ROLE', "")
        }
    }

    config["terragruntConfig"]['resources'].append({'cpu': task_definition.get("cpu", 0)})
    config["terragruntConfig"]['resources'].append({'memory': task_definition.get("memory", 0)})

    # Process each container definition
    for container in task_definition.get("containerDefinitions", []):
        terragrunt_container = {
            "name": container.get("name", ""),
            "image": container.get("image", ""),
            "environment": [],
            "ports": [],
            "dependencies": []
        }

        if "secrets" in container:
            for secret in container["secrets"]:
                secret_name = secret.get("valueFrom", "").split(":")[-1].rsplit("-", 1)[0]
                if secret_name not in config["terragruntConfig"]["secrets"]:
                    config["terragruntConfig"]["secrets"].append(
                        secret_name
                    )

        # Process environment variables
        if "environment" in container:
            for env in container["environment"]:
                terragrunt_container["environment"].append({
                    "name": env.get("name", ""),
                    "value": env.get("value", "")
                })

        # Process port mappings
        if "portMappings" in container:
            for port in container["portMappings"]:
                terragrunt_container["ports"].append({
                    "name": port.get("name", ""),
                    "hostPort": port.get("hostPort", 0),
                    "containerPort": port.get("containerPort", 0),
                    "protocol": port.get("protocol", "")
                })

        # Process dependencies (if any)
        if "dependsOn" in container:
            for dep in container["dependsOn"]:
                terragrunt_container["dependencies"].append({
                    "condition": dep.get("condition", ""),
                    "containerName": dep.get("containerName", "")
                })

        config["terragruntConfig"]["containers"].append(terragrunt_container)

    return config


def get_container_definitions():
    """
    Get container definitions from ECS service
    """
    # Required parameters
    cluster = os.getenv('ECS_CLUSTER')
    service = os.getenv('ECS_SERVICE')

    # Validate required parameters
    if not cluster:
        print("Error: ECS_CLUSTER is required")
        sys.exit(1)

    if not service:
        print("Error: ECS_SERVICE is required")
        sys.exit(1)

    try:
        # Get the ECS client
        ecs_client = get_boto3_client('ecs')

        # Get the service details
        print(f"Fetching service details for {service} in cluster {cluster}...")
        service_response = ecs_client.describe_services(
            cluster=cluster,
            services=[service]
        )

        if not service_response['services']:
            print(f"Error: Service {service} not found in cluster {cluster}")
            sys.exit(1)

        # Get the task definition ARN
        task_definition_arn = service_response['services'][0]['taskDefinition']
        print(f"Found task definition: {task_definition_arn}")

        # Get the task definition details
        task_def_response = ecs_client.describe_task_definition(
            taskDefinition=task_definition_arn
        )

        print("Converting to Terragrunt format...")
        response = convert_to_terragrunt_format(
            task_def_response['taskDefinition'],
            service
        )

        output_content = yaml.dump(response, default_flow_style=False, sort_keys=False)

        # Write to file if specified
        if os.getenv('OUTPUT_FILE'):
            with open(os.getenv('OUTPUT_FILE'), 'w') as f:
                f.write(output_content)
            print(f"Output written to {os.getenv('OUTPUT_FILE')}")
        else:
            print(output_content)

        print("✅ Successfully retrieved container definitions")
        return 0

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(get_container_definitions())
