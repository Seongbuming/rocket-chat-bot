import re
import datetime
import pytz
from rocket_chat import RocketChat
from github_api import GitHubAPI

class CommitTargets:
    def __init__(self, chat_api: RocketChat, rocket_chat_to_github_username=None):
        self.chat_api = chat_api
        self.rocket_chat_to_github_username = rocket_chat_to_github_username
        self.commit_targets = {}

    def generate_commit_targets_message(self, commit_data, date_range=None):
        if date_range:
            since, until = date_range
        else:
            since = datetime.datetime.now(pytz.timezone("Asia/Seoul"))
            until = since + datetime.timedelta(days=4)

        message = "<{0} ~ {1}>\n".format(
            since.strftime("%Y년 %m월 %d일"),
            until.strftime("%Y년 %m월 %d일"))

        for username, (_, _, completed, total) in commit_data.items():
            message += f"@{username} : {completed}/{total}\n"
        
        message += "커밋 후에 직접 수정해주세요(수정 권한 없을 시 연락)."

        return message

    def send_commit_targets_message(self, group_id):
        commit_data = {username: (0, target) for username, target in self.commit_targets.items()}
        message = self.generate_commit_targets_message(commit_data)
        self.chat_api.send_message_to_group(group_id, message)
    
    def update_commit_targets_message(self, group_id, github_api: GitHubAPI):
        last_message = self.get_latest_commit_targets(group_id)
        if last_message is not None:
            date_range = re.findall(r"<(\d{4}년 \d{2}월 \d{2}일) ~ (\d{4}년 \d{2}월 \d{2}일)>", last_message['msg'])
            if date_range:
                since_str, until_str = date_range[0]
                since = datetime.datetime.strptime(since_str, "%Y년 %m월 %d일")
                until = datetime.datetime.strptime(until_str, "%Y년 %m월 %d일")

                commit_counts_by_author = github_api.get_commit_counts_by_author(
                    "DVL-Sejong",
                    "augemented-analysis-for-industrial-data",
                    since,
                    until
                )
                print(commit_counts_by_author)

                for username in self.commit_targets:
                    github_username = self.rocket_chat_to_github_username[username]
                    commit_count = commit_counts_by_author.get(github_username, 0)

                    if commit_count < self.commit_targets[username][0]:
                        commit_count = self.commit_targets[username][0]
                    self.commit_targets[username] = (
                        self.commit_targets[username][0],
                        self.commit_targets[username][1],
                        commit_count,
                        self.commit_targets[username][1]
                    )
                
                last_message_id = last_message['_id']
                message = self.generate_commit_targets_message(self.commit_targets, (since, until))
                self.chat_api.update_message_from_group(group_id, last_message_id, message)

    def get_latest_commit_targets(self, group_id):
        messages = self.chat_api.get_latest_messages_from_group(group_id, 10)  # Get latest 10 messages
        for message in messages:
            user_targets = re.findall(r"@(\w+) : (\d+)/(\d+)", message['msg'])
            if user_targets:
                return message
        print("No valid commit target messages found!")
        return None

    def check_last_week_commits(self, group_id):
        last_message = self.get_latest_commit_targets(group_id)
        user_targets = re.findall(r"@(\w+) : (\d+)/(\d+)", last_message['msg'])

        self.commit_targets = {}
        for username, completed, total in user_targets:
            completed = int(completed)
            total = int(total)
            
            if completed < total:
                self.commit_targets[username] = (completed, total, 0, total * 2)
            else:
                self.commit_targets[username] = (completed, total, 0, 5)
    
        return self.commit_targets
