#!/usr/bin/env python3

import os
import sys
import boto3
import yaml
from datetime import datetime

def get_boto3_client(service_name='ecs'):
    """
    Create and return a boto3 client with appropriate authentication.
    """
    region = os.environ.get('AWS_REGION', os.environ.get('AWS_DEFAULT_REGION', 'eu-west-1'))
    profile_name = os.environ.get('AWS_PROFILE')
    role_arn = os.environ.get('AWS_ROLE_ARN')

    if role_arn:
        # Create an STS client to assume the role
        sts_client = boto3.client('sts', region_name=region)

        # Assume the role
        response = sts_client.assume_role(
            RoleArn=role_arn,
            RoleSessionName=f"ECSContainerDefinitionsPipe-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        )

        # Extract temporary credentials
        credentials = response['Credentials']

        # Create a new session with the assumed role credentials
        return boto3.client(
            service_name,
            region_name=region,
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken']
        )
    elif profile_name:
        # Use the specified AWS profile (including SSO profiles)
        session = boto3.Session(profile_name=profile_name)
        return session.client(service_name, region_name=region)
    else:
        # Standard credentials (from environment or instance profile)
        return boto3.client(service_name, region_name=region)


def convert_to_terragrunt_format(task_definition, service_name):
    """
    Convert ECS task definition to the required Terragrunt format.
    """
    # Initialize the terragrunt config structure
    config = {
        "deployment": {
            "extraEnv": os.environ.get('EXTRA_ENV', [])
        },
        "terragruntConfig": {
            "name": f"({service_name})",
            "secrets": [],
            "containers": [],
            "mainContainerName": "",
            "resources": [],
            "endpoints": os.environ.get('ENDPOINTS', []),
            "iamRole": os.environ.get('IAM_ROLE', "")
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
    cluster = os.environ.get('ECS_CLUSTER')
    service = os.environ.get('ECS_SERVICE')

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
        if os.environ.get('OUTPUT_FILE'):
            with open(os.environ.get('OUTPUT_FILE'), 'w') as f:
                f.write(output_content)
            print(f"Output written to {os.environ.get('OUTPUT_FILE')}")
        else:
            print(output_content)

        print("✅ Successfully retrieved container definitions")
        return 0

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(get_container_definitions())
