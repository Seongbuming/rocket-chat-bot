import requests

class GitHubAPI:
    def __init__(self):
        self.base_url = "https://api.github.com"

    def get_commits(self, owner, repo, since, until):
        url = f"{self.base_url}/repos/{owner}/{repo}/commits"
        params = {
            "since": since.isoformat(),
            "until": until.isoformat(),
            "per_page": 100
        }
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        all_commits = []

        while url:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            all_commits.extend(response.json())
            if 'next' in response.links:
                url = response.links['next']['url']
                params = {}
            else:
                url = None

        return all_commits

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
