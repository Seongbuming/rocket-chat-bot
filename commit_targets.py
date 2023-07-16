import re
import datetime
import pytz

class CommitTargets:
    def __init__(self, chat_api):
        self.chat_api = chat_api
        self.commit_targets = {}

    def send_commit_targets_message(self, group_id):
        now = datetime.datetime.now(pytz.timezone('Asia/Seoul'))
        future = now + datetime.timedelta(days=4)
        
        message = "<{0} ~ {1}>\n".format(
            now.strftime('%Y년 %m월 %d일'),
            future.strftime('%Y년 %m월 %d일'))

        for username, target in self.commit_targets.items():
            message += f"@{username} : 0/{target}\n"
        
        message += "커밋 후에 직접 수정해주세요(수정 권한 없을 시 연락)."

        self.chat_api.send_message_to_group(group_id, message)

    def get_latest_commit_targets(self, group_id):
        messages = self.chat_api.get_latest_messages_from_group(group_id, 10)  # Get latest 10 messages
        for message in messages:
            user_targets = re.findall(r"@(\w+) : (\d+)/(\d+)", message)
            if user_targets:
                return message
        print("No valid commit target messages found!")
        return None

    def check_last_week_commits(self, group_id):
        last_message = self.get_latest_commit_targets(group_id)
        user_targets = re.findall(r"@(\w+) : (\d+)/(\d+)", last_message)

        self.commit_targets = {}
        for username, completed, total in user_targets:
            completed = int(completed)
            total = int(total)
            
            if completed < total:
                self.commit_targets[username] = total * 2
            else:
                self.commit_targets[username] = 5
    
        return self.commit_targets
