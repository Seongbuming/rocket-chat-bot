import requests

class GitHubAPI:
    def __init__(self):
        self.base_url = "https://api.github.com"

    def get_commits(self, owner, repo, since, until):
        url = f"{self.base_url}/repos/{owner}/{repo}/commits"
        params = {
            "since": since.isoformat(),
            "until": until.isoformat()
        }
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        
        return response.json()

    def get_commit_counts_by_author(self, owner, repo, since, until):
        commits = self.get_commits(owner, repo, since, until)
        commit_counts = {}

        for commit in commits:
            if commit['author']:
                author = commit['author']['login']
            else:
                author = commit['commit']['author']['name']

            if author not in commit_counts:
                commit_counts[author] = 0
            commit_counts[author] += 1

        return commit_counts
