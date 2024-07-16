import unittest
from unittest.mock import patch, Mock
import os
from pipe.pipe import Config, NewRelicClient, V1Deployment, V2Deployment, NewRelicDeploymentPipe, v1_schema, v2_schema

class TestConfig(unittest.TestCase):
    @patch.dict(os.environ, {
        'NEW_RELIC_API_KEY': '12345',
        'APPLICATION_NAME': 'MyApp',
        'COMPONENT_TYPE': 'backend',
        'ENVIRONMENT': 'production',
        'SHORT_REGION': 'us-west-2',
        'DEPLOYMENT_REVISION': 'rev123'
    })
    def test_load_config(self):
        """Test that environment variables are loaded correctly."""
        schema = {
            'NEW_RELIC_API_KEY': {'type': 'string', 'required': True},
            'APPLICATION_NAME': {'type': 'string', 'required': True},
            'COMPONENT_TYPE': {'type': 'string', 'required': True},
            'ENVIRONMENT': {'type': 'string', 'required': True},
            'SHORT_REGION': {'type': 'string', 'required': True},
            'DEPLOYMENT_REVISION': {'type': 'string', 'required': True}
        }
        config = Config(schema)
        self.assertEqual(config.get('NEW_RELIC_API_KEY'), '12345')

class TestNewRelicClient(unittest.TestCase):
    def setUp(self):
        self.api_key = '12345'
        self.client = NewRelicClient(self.api_key)

    @patch('requests.get')
    def test_search_applications(self, mock_get):
        """Test that search_applications sends a request to the correct URL with correct headers."""
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'applications': []}

        self.client.search_applications('MyApp%production%us-west-2%backend')
        mock_get.assert_called_once_with(
            'https://api.newrelic.com/v2/applications.json',
            headers={'X-Api-Key': '12345', 'Content-Type': 'application/json'},
            params={'filter[name]': 'MyApp%production%us-west-2%backend'}
        )

class TestV1Deployment(unittest.TestCase):
    @patch('pipe.pipe.NewRelicClient')
    def test_run_v1_deployment(self, mock_client_class):
        client = mock_client_class.return_value
        client.create_deployment_marker.return_value = None  # Assume this function returns None

        config = Mock(spec=Config)
        config.get.return_value = '12345'

        runner = V1Deployment(client, config)
        runner.run()

        client.create_deployment_marker.assert_called_once()

class TestV2Deployment(unittest.TestCase):
    @patch('pipe.pipe.NewRelicClient')
    def test_run_v2_deployment(self, mock_client_class):
        client = mock_client_class.return_value
        client.search_applications.return_value = [{'id': 'app_id_1', 'name': 'MyApp'}]
        client.create_deployment_marker.return_value = None

        config = Mock(spec=Config)
        config.get_app_name_pattern.return_value = 'MyApp%production%us-west-2%backend'
        config.get.side_effect = lambda key: {'DEPLOYMENT_USER': 'bitbucket.pipeline', 'DEPLOYMENT_REVISION': 'rev123'}[key]

        runner = V2Deployment(client, config)
        runner.run()

        client.search_applications.assert_called_once_with('MyApp%production%us-west-2%backend')
        client.create_deployment_marker.assert_called_once_with('app_id_1', 'bitbucket.pipeline', 'rev123', 'Deployed new version')

class TestNewRelicDeploymentPipe(unittest.TestCase):
    @patch('pipe.pipe.NewRelicDeploymentPipe.run')
    @patch.dict(os.environ, {
        'NEW_RELIC_API_KEY': '12345',
        'NEW_RELIC_APPLICATION_ID': 'app123',
        'DEPLOYMENT_REVISION': 'rev123'
    })
    def test_pipe_initialization_v1(self, mock_run):
        """Test that the pipe initializes the correct deployment class based on environment variables."""
        mock_run.return_value = None
        with patch('pipe.pipe.V1Deployment', spec=V1Deployment) as mock_v1_deployment_class:
            pipe = NewRelicDeploymentPipe(v1_schema, {}, mock_v1_deployment_class)
            self.assertIsInstance(pipe.deployment, V1Deployment)

    @patch('pipe.pipe.NewRelicDeploymentPipe.run')
    @patch.dict(os.environ, {
        'NEW_RELIC_API_KEY': '12345',
        'APPLICATION_NAME': 'MyApp',
        'COMPONENT_TYPE': 'backend',
        'ENVIRONMENT': 'production',
        'SHORT_REGION': 'us-west-2',
        'DEPLOYMENT_REVISION': 'rev123'
    })
    def test_pipe_initialization_v2(self, mock_run):
        """Test that the pipe initializes the correct deployment class based on environment variables."""
        mock_run.return_value = None
        with patch('pipe.pipe.V2Deployment', spec=V2Deployment) as mock_v2_deployment_class:
            pipe = NewRelicDeploymentPipe(v2_schema, {}, mock_v2_deployment_class)
            self.assertIsInstance(pipe.deployment, V2Deployment)


if __name__ == '__main__':
    unittest.main()