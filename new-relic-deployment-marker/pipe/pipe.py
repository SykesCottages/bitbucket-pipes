import os
import requests
from typing import Dict, List, Any, Type
from abc import ABC, abstractmethod
from cerberus import Validator
from bitbucket_pipes_toolkit import Pipe, get_logger
import yaml

logger = get_logger()

v2_schema = {
    'NEW_RELIC_API_KEY': {'type': 'string', 'required': True},
    'APPLICATION_NAME': {'type': 'string', 'required': True},
    'COMPONENT_TYPE': {'type': 'string', 'required': True},
    'ENVIRONMENT': {'type': 'string', 'required': True},
    'SHORT_REGION': {'type': 'string', 'required': True},
    'DEPLOYMENT_USER': {'type': 'string', 'required': False, 'default': 'bitbucket.pipeline'},
    'DEPLOYMENT_REVISION': {'type': 'string', 'required': True},
}

v1_schema = {
    'NEW_RELIC_API_KEY': {'type': 'string', 'required': True},
    'NEW_RELIC_APPLICATION_ID': {'type': 'string', 'required': True},
    'DEPLOYMENT_REVISION': {'type': 'string', 'required': True},
    'DEPLOYMENT_USER': {'type': 'string', 'required': False, 'default': 'bitbucket.pipeline'},
}

class Config:
    def __init__(self, schema: Dict[str, Any]) -> None:
        self.validator = Validator(schema)
        self.config = self.load_config()

    def load_config(self) -> Dict[str, str]:
        config = {key: os.getenv(key, default=value.get('default')) for key, value in self.validator.schema.items()}
        if not self.validator.validate(config):
            raise ValueError(f"Configuration validation error: {self.validator.errors}")
        return self.validator.document

    def get(self, key: str) -> str:
        return self.config[key]

    def get_app_name_pattern(self) -> str:
        return f'%{self.get("APPLICATION_NAME")}%{self.get("ENVIRONMENT")}%{self.get("SHORT_REGION")}%{self.get("COMPONENT_TYPE")}'

class NewRelicClient:
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key
        self.base_url = 'https://api.newrelic.com/v2/'

    def search_applications(self, app_name_pattern: str) -> List[Dict[str, Any]]:
        headers = {
            'X-Api-Key': self.api_key,
            'Content-Type': 'application/json'
        }
        url = f'{self.base_url}applications.json'
        params = {
            'filter[name]': app_name_pattern
        }
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()['applications']

    def create_deployment_marker(self, app_id: str, user: str, revision: str, description: str) -> None:
        url = f'{self.base_url}applications/{app_id}/deployments.json'
        headers = {
            'X-Api-Key': self.api_key,
            'Content-Type': 'application/json'
        }
        payload = {
            'deployment': {
                'revision': revision,
                'changelog': description,
                'user': user
            }
        }
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()

class DeploymentRunner(ABC):
    def __init__(self, client: NewRelicClient, config: Config) -> None:
        self.client = client
        self.config = config

    @abstractmethod
    def run(self) -> None:
        pass

class V1Deployment(DeploymentRunner):
    def run(self) -> None:
        logger.info("Starting New Relic Deployment with v1 schema")
        
        app_id = self.config.get('NEW_RELIC_APPLICATION_ID')
        user = self.config.get('DEPLOYMENT_USER')
        revision = self.config.get('DEPLOYMENT_REVISION')
        description = "Deployed new version with v1 schema"

        try:
            self.client.create_deployment_marker(app_id, user, revision, description)
            logger.info(f"Deployment marker created for Application ID {app_id} with v1 schema")
        except requests.RequestException as e:
            logger.error(f"Error creating deployment marker for Application ID {app_id}: {str(e)}")
            raise

class V2Deployment(DeploymentRunner):
    def run(self) -> None:
        logger.info("Starting New Relic Deployment with v2 schema")
        app_name_pattern = self.config.get_app_name_pattern()
        logger.info(f"Searching applications with pattern: {app_name_pattern}")

        try:
            applications = self.client.search_applications(app_name_pattern)
        except requests.RequestException as e:
            logger.error(f"Error searching applications: {str(e)}")
            raise

        for app in applications:
            app_id = app['id']
            app_name = app['name']
            logger.info(f"Application ID: {app_id}, Name: {app_name}")

            try:
                deployment_description = "Deployed new version"
                self.client.create_deployment_marker(
                    app_id, self.config.get('DEPLOYMENT_USER'), self.config.get('DEPLOYMENT_REVISION'), deployment_description)
                logger.info(f"Deployment marker created for Application ID {app_id}")
            except requests.RequestException as e:
                logger.error(f"Error creating deployment marker for Application ID {app_id}: {str(e)}")
                raise

class NewRelicDeploymentPipe(Pipe):
    def __init__(self, schema: Dict[str, Any], pipe_metadata: Dict[str, Any], deployment_cls: Type[DeploymentRunner]) -> None:
        super().__init__(schema=schema, pipe_metadata=pipe_metadata)
        self.config = Config(schema)
        self.client = NewRelicClient(self.config.get('NEW_RELIC_API_KEY'))
        self.deployment = deployment_cls(self.client, self.config)

    def run(self) -> None:
        self.deployment.run()

if __name__ == '__main__':
    with open('/pipe.yml', 'r') as metadata_file:
        metadata = yaml.safe_load(metadata_file.read())
        
        if 'NEW_RELIC_APPLICATION_ID' in os.environ:
            schema = v1_schema
            deployment_cls = V1Deployment
        else:
            schema = v2_schema
            deployment_cls = V2Deployment
        
        pipe = NewRelicDeploymentPipe(schema=schema, pipe_metadata=metadata, deployment_cls=deployment_cls)
        pipe.run()