import config
from rocket_chat import RocketChat
from commit_targets import CommitTargets

def main():
    chat_api = RocketChat(config.BASE_URL, config.USERNAME, config.PASSWORD)
    commit_targets = CommitTargets(chat_api)
    group_id = chat_api.get_group_id("opensource")
    commit_targets_dict = commit_targets.check_last_week_commits(group_id)
    commit_targets.send_commit_targets_message(group_id, commit_targets_dict)

if __name__ == "__main__":
    main()
