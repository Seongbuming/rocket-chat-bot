import re
import datetime
import pytz
from dateutil.relativedelta import relativedelta, MO
from rocket_chat import RocketChat
from github_api import GitHubAPI

class CommitTargets:
    def __init__(self, chat_api: RocketChat, github_api: GitHubAPI, repositories=[], rocket_chat_to_github_username=None):
        self.chat_api = chat_api
        self.github_api = github_api
        self.commit_targets = {}
        self.repositories = repositories
        self.rocket_chat_to_github_username = rocket_chat_to_github_username

    def generate_commit_targets_message(self, commit_data, since: datetime.datetime, until: datetime.datetime):
        message = "<{0} ~ {1}>\n".format(
            since.strftime("%Y년 %m월 %d일"),
            until.strftime("%Y년 %m월 %d일"))

        for username, (_, _, completed, total) in commit_data.items():
            message += f"@{username} : {completed}/{total}\n"
        
        message += "1시간마다 자동으로 갱신됩니다."

        return message

    def send_commit_targets_message(self, group_id):
        now = datetime.datetime.now(pytz.timezone("Asia/Seoul"))
        since = (now + relativedelta(weekday=MO(-1))).replace(hour=0, minute=0, second=0, microsecond=0)
        until = since + datetime.timedelta(days=4)

        commit_counts_by_author = self.calculate_commit_counts(since, until)

        for username in self.commit_targets:
            github_username = self.rocket_chat_to_github_username[username]
            commit_count = commit_counts_by_author.get(github_username, 0)
            self.commit_targets[username] = [
                commit_count,
                self.commit_targets[username][3],
                commit_count,
                self.commit_targets[username][3]
            ]
        
        message = self.generate_commit_targets_message(self.commit_targets, since, until)
        self.chat_api.send_message_to_group(group_id, message)
    
    def update_commit_targets_message(self, group_id):
        last_message = self.get_latest_commit_targets(group_id)
        if last_message is not None:
            date_range = re.findall(r"<(\d{4}년 \d{2}월 \d{2}일) ~ (\d{4}년 \d{2}월 \d{2}일)>", last_message['msg'])
            if date_range:
                since_str, until_str = date_range[0]
                since = datetime.datetime.strptime(since_str, "%Y년 %m월 %d일")
                until = datetime.datetime.strptime(until_str, "%Y년 %m월 %d일")

                commit_counts_by_author = self.calculate_commit_counts(since, until)

                for username in self.commit_targets:
                    github_username = self.rocket_chat_to_github_username[username]
                    commit_count = commit_counts_by_author.get(github_username, 0)

                    # 사용자가 직접 기재한 커밋 카운트를 우선으로 함
                    if commit_count < self.commit_targets[username][0]:
                        commit_count = self.commit_targets[username][0]
                    self.commit_targets[username] = (
                        self.commit_targets[username][0],
                        self.commit_targets[username][1],
                        commit_count,
                        self.commit_targets[username][1]
                    )
                
                last_message_id = last_message['_id']
                message = self.generate_commit_targets_message(self.commit_targets, since, until)
                self.chat_api.update_message_from_group(group_id, last_message_id, message)

    def calculate_commit_counts(self, since, until):
        commit_counts_by_author = {}

        for repo in self.repositories:
            commit_counts = self.github_api.get_commit_counts_by_author(
                "DVL-Sejong",
                repo,
                since - datetime.timedelta(days=1),
                until + datetime.timedelta(days=1)
            )
            for author, count in commit_counts.items():
                if author in commit_counts_by_author:
                    commit_counts_by_author[author] += count
                else:
                    commit_counts_by_author[author] = count
                    
        return commit_counts_by_author
    
    def parse_commit_data_from_message(self, message):
        user_targets = re.findall(r"@(\w+) : (\d+)/(\d+)", message['msg'])
        commit_data = {}

        for username, completed, total in user_targets:
            completed = int(completed)
            total = int(total)

            if completed < total:
                commit_data[username] = [completed, total, 0, total + 2]
            else:
                commit_data[username] = [completed, total, 0, 5]

        return commit_data

    def get_latest_commit_targets(self, group_id):
        messages = self.chat_api.get_latest_messages_from_group(group_id, 20)

        for message in messages:
            if re.search(r"@(\w+) : (\d+)/(\d+)", message['msg']):
                return message
        
        print("No valid commit target messages found!")
        return None

    def check_last_week_commits(self, group_id):
        last_message = self.get_latest_commit_targets(group_id)
        self.commit_targets = self.parse_commit_data_from_message(last_message)

        return self.commit_targets
