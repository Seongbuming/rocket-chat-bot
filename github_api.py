import requests

class GitHubApi:
    def __init__(self, access_token):
        self.headers = {'Authorization': f'token {access_token}'}

    def get_commit_count(self, repo_owner, repo_name, author, since, until):
        commit_count = 0
        since_str = since.isoformat()+'Z'
        until_str = until.isoformat()+'Z'
        commit_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/commits?author={author}&since={since_str}&until={until_str}"
        commit_data = requests.get(commit_url, headers=self.headers).json()

        for commit in commit_data:
            if commit['commit']['author']['name'] == author:
                commit_count += 1

        return commit_count
