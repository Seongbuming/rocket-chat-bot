import os
import argparse
import json
from rocket_chat import RocketChat
from commit_targets import CommitTargets
from github_api import GitHubAPI

def send(rocket_chat: RocketChat):
    commit_targets = CommitTargets(rocket_chat)
    group_id = rocket_chat.get_group_id("opensource")
    commit_targets.check_last_week_commits(group_id)
    commit_targets.send_commit_targets_message(group_id)

def update(rocket_chat: RocketChat, github: GitHubAPI):
    commit_targets = CommitTargets(rocket_chat, json.loads(os.getenv("USER_MAPPING")))
    group_id = rocket_chat.get_group_id("opensource")
    commit_targets.check_last_week_commits(group_id)
    commit_targets.update_commit_targets_message(group_id, github)

if __name__ == "__main__":
    rocket_chat = RocketChat(
        base_url=os.getenv("ROCKET_CHAT_INSTANCE"),
        username=os.getenv("USERNAME"),
        password=os.getenv("PASSWORD"),
        debug=os.getenv("DEBUG")
    )
    github = GitHubAPI()

    parser = argparse.ArgumentParser()
    parser.add_argument("--send", action="store_true", help="Run to send the message.")
    parser.add_argument("--update", action="store_true", help="Run to update the message.")
    args = parser.parse_args()

    if args.send:
        send(rocket_chat)
    elif args.update:
        update(rocket_chat, github)
    else:
        parser.print_help()
