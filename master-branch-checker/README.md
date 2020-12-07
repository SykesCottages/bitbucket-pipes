# Bitbucket Master Branch Checker

Check if current branch is behind current master by a few commits and prevents exits the pipeline execution if it is.

## YAML Definition

Add the following snippet to the script section of your `bitbucket-pipelines.yml` file:

```yaml
- pipe: sykescottages/master-branch-checker
```