# Hello World

Just a hello world script to help me test the end to end process of writing, updating and deploying a pipe

## YAML Definition

Add the following snippet to the script section of your `bitbucket-pipelines.yml` file:

```yaml
- pipe: docker://sykescottages/bitbucket-pipes:hello-world    
    variables:
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
    - pipe: docker://sykescottages/bitbucket-pipes:hello-world
    variables:
      THING_TO_ECHO: "Hello World"
```

