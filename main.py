import os
from rocket_chat import RocketChat
from commit_targets import CommitTargets

def main():
    rocket_chat = RocketChat(
        base_url=os.getenv('ROCKET_CHAT_INSTANCE'),
        username=os.getenv('USERNAME'),
        password=os.getenv('PASSWORD')
    )

    commit_targets = CommitTargets(rocket_chat)

    group_id = rocket_chat.get_group_id('opensource')
    commit_targets.check_last_week_commits(group_id)
    commit_targets.send_commit_targets_message(group_id)

if __name__ == "__main__":
    main()
