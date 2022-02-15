# New Relic Deployment Marker
Mark new deployments in New Relic with this Bitbucket Pipe

## YAML Definition

Add the following snippet to the script section of your `bitbucket-pipelines.yml` file:

```yaml
- pipe: docker://sykescottages/bitbucket-pipes:new-relic-deployment-marker
    NEW_RELIC_API_KEY: '<string>'
    NEW_RELIC_APPLICATION_ID: '<string>'
    NEW_RELIC_REGION: '<string>'
    DEPLOYMENT_USER: '<string>'
    DEPLOYMENT_REVISION: '<string>'
```

## Variables

| Variable              | Usage                                                       |
| --------------------- | ----------------------------------------------------------- |
| NEW_RELIC_API_KEY (*)         | New Relic API Key |
| NEW_RELIC_APPLICATION_ID (*)  | The ID of the application you want to tag. |
| DEPLOYMENT_REVISION (*)        | The revision or the deployment ID to mark in NR|
| NEW_RELIC_REGION              | Region the data is in. Defaults to US |
| DEPLOYMENT_USER     | User responsible for this deployment, defaults to bitbucket.pipeline |
(*) = required variable. This variable needs to be specified always when using the pipe.
