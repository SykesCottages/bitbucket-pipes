import os
import re

import tiktoken
import yaml
import requests

from typing import Dict, Any

from bitbucket_pipes_toolkit import Pipe, get_logger, fail
from snakemd import Document, Table, Inline

from code_review.crew import CodeReview

logger = get_logger()
schema = {
    'OPENAI_API_KEY': {'type': 'string', 'required': True},
    'BITBUCKET_ACCESS_TOKEN': {'type': 'string', 'required': True},
    'MODEL': {'type': 'string', 'required': True, 'allowed': ['gpt-4o-mini', 'gpt-4o', 'o3-mini', 'o3']},
    'KNOWLEDGE_FILE_PATH': {'type': 'string', 'required': False},
    'MAX_INPUT_TOKENS': {'type': 'integer', 'required': False, 'default': 10000},
    'MAX_SUGGESTIONS': {'type': 'integer', 'required': False, 'default': 10},
    'MIN_SEVERITY_LIMIT': {'type': 'integer', 'required': False, 'default': 0},
    'SUGGEST_CODE': {'type': 'boolean', 'required': False, 'default': False},
}

class BitbucketApiService:
    BITBUCKET_API_BASE_URL = "https://api.bitbucket.org/2.0"
    DIFF_DELIMITER = "diff --git a/"

    def __init__(self, auth, workspace, repo_slug):
        self.auth = auth
        self.workspace = workspace
        self.repo_slug = repo_slug

    def get_last_pull_request_build(self, branch):
        url_diff = f"{self.BITBUCKET_API_BASE_URL}/repositories/{self.workspace}/{self.repo_slug}/pipelines?target.branch={branch}&target.selector.type=PULLREQUESTS&sort=-run_creation_date"
        response = requests.request("GET", url_diff, auth=self.auth)
        response.raise_for_status()
        json_response = response.json()

        if 'values' in json_response and len(json_response['values']) > 1:
            return json_response['values'][1]
        else:
            return None  # Return None if the second value does not exist

    def get_pull_request(self, pull_request_id):
        url_diff = f"{self.BITBUCKET_API_BASE_URL}/repositories/{self.workspace}/{self.repo_slug}/pullrequests/{pull_request_id}"
        response = requests.request("GET", url_diff, auth=self.auth)
        response.raise_for_status()
        return response.json()

    def get_pull_request_commits(self, pull_request_id):
        url_diff = f"{self.BITBUCKET_API_BASE_URL}/repositories/{self.workspace}/{self.repo_slug}/pullrequests/{pull_request_id}/commits"
        response = requests.request("GET", url_diff, auth=self.auth)
        response.raise_for_status()
        return response.json()

    def get_pull_request_diffs(self, pull_request_id):
        url_diff = f"{self.BITBUCKET_API_BASE_URL}/repositories/{self.workspace}/{self.repo_slug}/pullrequests/{pull_request_id}/diff"
        response = requests.request("GET", url_diff, auth=self.auth)
        response.raise_for_status()
        return response.text

    def get_commit_diff(self, commit_hash):
        url_diff = f"{self.BITBUCKET_API_BASE_URL}/repositories/{self.workspace}/{self.repo_slug}/diff/{commit_hash}"
        response = requests.request("GET", url_diff, auth=self.auth)
        response.raise_for_status()
        return response.text

    def add_comment(self, pull_request_id, payload):
        url_comment = f"{self.BITBUCKET_API_BASE_URL}/repositories/{self.workspace}/{self.repo_slug}/pullrequests/{pull_request_id}/comments"
        response = requests.request("POST", url_comment, auth=self.auth, json=payload)
        response.raise_for_status()
        return response.json()

    def get_approval(self, pull_request_id):
        url_comment = f"{self.BITBUCKET_API_BASE_URL}/repositories/{self.workspace}/{self.repo_slug}/pullrequests/{pull_request_id}/approve"
        response = requests.request("POST", url_comment, auth=self.auth)
        response.raise_for_status()
        return response.json()

    def unapprove(self, pull_request_id):
        url_comment = f"{self.BITBUCKET_API_BASE_URL}/repositories/{self.workspace}/{self.repo_slug}/pullrequests/{pull_request_id}/approve"
        requests.request("DELETE", url_comment, auth=self.auth)


class CodeReviewPipe(Pipe):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.auth_method_bitbucket = self.resolve_auth()

        # Bitbucket
        self.workspace = os.getenv('BITBUCKET_WORKSPACE')
        self.repo_slug = os.getenv('BITBUCKET_REPO_SLUG')
        self.bitbucket_client = BitbucketApiService(
            self.auth_method_bitbucket, self.workspace, self.repo_slug)

    def num_tokens_from_string(self, string: str, encoding_name: str) -> int:
        """Returns the number of tokens in a text string."""
        encoding = tiktoken.get_encoding(encoding_name)
        num_tokens = len(encoding.encode(string))
        return num_tokens

    def run(self):
        super().run()
        self.log_info('Executing the pipe...')

        pull_request_id = os.getenv("BITBUCKET_PR_ID")
        if pull_request_id is None:
            self.fail(
                'BITBUCKET_PR_ID variable is required! '
                'Pullrequest ID variable is not detected in the environment. '
                'Make sure the pipe is executed on a pull request triggered build: '
                'https://support.atlassian.com/bitbucket-cloud/docs/pipeline-start-conditions/#Pull-Requests'
            )

        pull_reqeust = self.bitbucket_client.get_pull_request(pull_request_id)
        last_pull_request_build = self.bitbucket_client.get_last_pull_request_build(pull_reqeust['source']['branch']['name'])

        # If we've had no build prior to this one, review the entire PR - If not, then only review non merge commits
        if last_pull_request_build is None:
            self.log_info(f"Pull Request has no previous build, going to do a full review of pull request: {pull_request_id}")
            diff_to_review = self.bitbucket_client.get_pull_request_diffs(pull_request_id)
        else:
            self.log_info(
                f"Pull Request has a previous build, going to do a partial review of pull request: {pull_request_id}")

            last_build_commit = last_pull_request_build['target']['commit']['hash']
            pull_reqeust_commits = self.bitbucket_client.get_pull_request_commits(pull_request_id)
            commits_to_review = []
            for commit in pull_reqeust_commits['values']:
                if commit['hash'] == last_build_commit:
                    break

                if len(commit['parents']) > 1:
                    continue

                commits_to_review.append(commit['hash'])

            # Reverse the commits so we have them in order of oldest first
            commits_to_review.reverse()
            diff_to_review = []
            for commit_to_review in commits_to_review:
                diff_to_review.append(f"--- Commit Hash: {commit_to_review} ---")
                diff_to_review.append(self.bitbucket_client.get_commit_diff(commit_to_review))

            diff_to_review = '\n'.join(diff_to_review)

        if not diff_to_review:
            self.log_warning(f"No files for code review.")
            self.success(message='Pipe is stopped.', do_exit=True)

        number_of_tokens = self.num_tokens_from_string(diff_to_review, "o200k_base")

        input_token_limit = self.get_variable('MAX_INPUT_TOKENS')
        # Check for sensible max tokens, add pipe variable for this
        if number_of_tokens > input_token_limit:
            self.log_warning(f"Max input tokens exceeded limit of {input_token_limit}. Actual count of tokens: {number_of_tokens}.")
            self.success(message='Pipe is stopped.', do_exit=True)

        max_suggestions = self.get_variable('MAX_SUGGESTIONS')
        min_severity_limit = self.get_variable('MIN_SEVERITY_LIMIT')
        inputs = {
            'code_to_review': diff_to_review,
            'max_suggestion_count': max_suggestions,
            'min_severity_limit': min_severity_limit
        }

        self.log_info(
            f"Generating a max suggestion count of: {max_suggestions}")

        output = (CodeReview()
                  .crew(knowledge_source_file=self.get_variable('KNOWLEDGE_FILE_PATH'))
                  .kickoff(inputs=inputs))

        self.log_info(f"Tokens Used: {output.token_usage}")

        # Toggle between formats if the suggest code flag is set
        if self.get_variable('SUGGEST_CODE'):
            comment = self.generate_issues_with_code_markdown_table(output.json_dict)
        else:
            comment = self.generate_all_issues_markdown_table(output.json_dict)

        self.make_ai_approval_based_on_severity(output.json_dict, pull_request_id)
        added_suggestions = self.add_comment(pull_request_id, comment)
        ui_pull_request_url = f"https://bitbucket.org/{self.workspace}/{self.repo_slug}/pull-requests/{pull_request_id}"
        self.success(message=f"🤖 Successfully added {added_suggestions} comments to the pull request: {ui_pull_request_url} 🤖")

    def make_ai_approval_based_on_severity(self, output, pull_request_id):
        approve = True

        for issue in output['issues']:
            if int(issue['severity']) > 3:
                approve = False

        if approve:
            self.bitbucket_client.get_approval(pull_request_id)
        else:
            self.bitbucket_client.unapprove(pull_request_id)

        return 1

    def generate_all_issues_markdown_table(self, output):
        doc = Document()
        doc = self.generate_summary_of_changes(doc, output['summary_of_changes'])
        header = self.get_table_header()
        data = []
        for issue in output['issues']:
            data.append([
                issue['title'],
                issue['file']['full_path'] + "#" + str(issue['file']['new_line']),
                str(int(issue['severity'])) + " (" + issue['state'] + ")",
                issue['description'],
            ])

        doc.add_table(
            header,
            data,
        )
        return str(doc)

    def generate_issues_with_code_markdown_table(self, output):
        doc = Document()
        doc = self.generate_summary_of_changes(doc, output['summary_of_changes'])
        header = self.get_table_header()
        for issue in output['issues']:
            doc.add_table(header, [
                [
                    issue['title'],
                    issue['file']['full_path'] + "#" + str(issue['file']['new_line']),
                    str(int(issue['severity'])) + " (" + issue['state'] + ")",
                    issue['description'],
                ]
            ])
            doc.add_heading('Original', 3)
            doc.add_code(issue['code']['before'])

            doc.add_heading('Recommended Change', 3)
            doc.add_code(issue['code']['after'])

        return str(doc)

    def generate_summary_of_changes(self, doc: Document, summary):
        doc.add_heading("Summary of Changes", 3)
        doc.add_paragraph(summary)
        return doc

    def get_table_header(self):
        return ["❓ Suggestion", "📁 Affected File", "🚨 Severity (1-10)", "📜 Description"]

    def add_comment(self, pull_request_id, data):
        payload = {
            'content': {
                'raw': data
            }
        }

        self.bitbucket_client.add_comment(pull_request_id, payload)

        return 1

if __name__ == '__main__':
    with open('/pipe.yml', 'r') as metadata_file:
        metadata = yaml.safe_load(metadata_file.read())
        pipe = CodeReviewPipe(schema=schema, pipe_metadata=metadata)
        pipe.run()

