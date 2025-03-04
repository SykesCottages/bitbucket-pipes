# Code Review Agent
Review Code using CrewAI

## YAML Definition
### Variables

| Variable                   | Usage                                       |
|----------------------------|---------------------------------------------|
| OPENAI_API_KEY (*)         | OpenAI API Key                           |
| BITBUCKET_ACCESS_TOKEN (*) | Access token to read and write to bitbucket |
| MODEL (*)                  | The OpenAI Model                            |

Add the following snippet to the script section of your `bitbucket-pipelines.yml` file:

```yaml
- pipe: docker://sykescottages/bitbucket-pipes:code-review-agent
    OPENAI_API_KEY: '<string>'
    BITBUCKET_ACCESS_TOKEN: '<string>'
    MODEL: '<string>'
```
