# New Relic Deployment Marker
Mark new deployments in New Relic with this Bitbucket Pipe

## Important
If you do not follow the new relic naming convention the deployment marker might not work. Make sure you're following the naming convention when generating an APM.

## YAML Definition
### Variables

| Variable              | Usage                                                       |
| --------------------- | ----------------------------------------------------------- |
| NEW_RELIC_API_KEY (*) | New Relic API Key |
| APPLICATION_NAME (*)  | The name of the application in New Relic to find the ID  |
| ENVIRONMENT(*)        | Environment name where the deployment is taking place (e.g., production, staging). |
| COMPONENT_TYPE (*)    | The component type of the application in New Relic. Valid options are Web, Cmd, and Cron.|
| SHORT_REGION (*)      | The region where the application is running. (e.g, Ew1, As2) |
| DEPLOYMENT_REVISION (*)| The revision or the deployment ID to mark in NR|
| DEPLOYMENT_USER     | User responsible for this deployment, defaults to bitbucket.pipeline |
(*) = required variable. This variable needs to be specified always when using the pipe.

Add the following snippet to the script section of your `bitbucket-pipelines.yml` file:

```yaml
- pipe: docker://sykescottages/bitbucket-pipes:new-relic-deployment-marker
    NEW_RELIC_API_KEY: '<string>'
    APPLICATION_NAME: '<string>'
    COMPONENT_TYPE: '<string>'
    ENVIRONMENT: '<string>' 
    SHORT_REGION: '<string>' 
    DEPLOYMENT_REVISION: '<string>' 
```
