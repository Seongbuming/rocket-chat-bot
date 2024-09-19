import os
import argparse
import json
from rocket_chat import RocketChat
from commit_targets import CommitTargets
from github_api import GitHubAPI
from server_status import ServerStatus

REPOSITORIES = json.loads(os.getenv("REPOSITORIES"))
USER_MAPPING = json.loads(os.getenv("USER_MAPPING"))

def send(rocket_chat: RocketChat, github: GitHubAPI):
    rocket_chat.login()
    commit_targets = CommitTargets(rocket_chat, github, REPOSITORIES, USER_MAPPING)
    group_id = rocket_chat.get_group_id("opensource")
    commit_targets.check_last_week_commits(group_id)
    commit_targets.send_commit_targets_message(group_id)

def update(rocket_chat: RocketChat, github: GitHubAPI):
    rocket_chat.login()
    commit_targets = CommitTargets(rocket_chat, github, REPOSITORIES, USER_MAPPING)
    group_id = rocket_chat.get_group_id("opensource")
    commit_targets.check_last_week_commits(group_id)
    commit_targets.update_commit_targets_message(group_id)

def status(rocket_chat: RocketChat):
    try:
        rocket_chat.login()
        group_id_opensource = rocket_chat.get_group_id("opensource")
        server_status = ServerStatus(rocket_chat)
        server_status.send_status_change(group_id_opensource)
    except Exception:
        server_status = ServerStatus(rocket_chat)
        server_status.save_current_status("down")
        print("VISLAB Rocket.Chat is still down.")

if __name__ == "__main__":
    rocket_chat = RocketChat(
        base_url=os.getenv("ROCKET_CHAT_INSTANCE"),
        username=os.getenv("USERNAME"),
        password=os.getenv("PASSWORD"),
        debug=os.getenv("DEBUG")
    )

    parser = argparse.ArgumentParser()
    parser.add_argument("--send", action="store_true", help="Run to send the message.")
    parser.add_argument("--update", action="store_true", help="Run to update the message.")
    parser.add_argument("--status", action="store_true", help="Run to check server status.")
    args = parser.parse_args()

    if args.send:
        github = GitHubAPI()
        send(rocket_chat, github)
    elif args.update:
        github = GitHubAPI()
        update(rocket_chat, github)
    elif args.status:
        status(rocket_chat)
    else:
        parser.print_help()
