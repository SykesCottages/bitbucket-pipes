# Bitbucket EC2 Instance Tagger

Tag running AWS EC2 Instance ready for deployment in Bitbucket pipeline.

## YAML Definition

Add the following snippet to the script section of your `bitbucket-pipelines.yml` file:

```yaml
- pipe: sykescottages/hello-world
    THING_TO_ECHO: '<string>'
```

## Variables

| Variable              | Usage                                                       |
| --------------------- | ----------------------------------------------------------- |
| THING_TO_ECHO| Something to echo out |

## Examples

Example pipe yaml

```yaml
script:
  - pipe: sykescottages/hello-world
    variables:
      THING_TO_ECHO: "Hello World"
```

