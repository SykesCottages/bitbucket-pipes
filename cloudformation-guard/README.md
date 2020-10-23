# CloudFormation Guard 
Run validation on the CloudFormation Template based on a ruleset.

## YAML Definition

Add the following snippet to the script section of your `bitbucket-pipelines.yml` file:

```yaml
- pipe: sykescottages/cloudformation-guard
    CLOUDFORMATION_RULESET_FILE: '<string>'
    CLOUDFORMATION_TEMPLATE_FILE: '<string>'
```

## Variables

| Variable              | Usage                                                       |
| --------------------- | ----------------------------------------------------------- |
| CLOUDFORMATION_RULESET_FILE (*)         | Rules that we should validate the template file against |
| CLOUDFORMATION_TEMPLATE_FILE (*)  | Cloudformation Template/Output of CDK Synth |
(*) = required variable. This variable needs to be specified always when using the pipe.
