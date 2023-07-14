import requests
import urllib3
import json

class RocketChat:
    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.auth_token = None
        self.user_id = None
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.login()

    def login(self):
        url = f"https://{self.base_url}/api/v1/login"
        payload = {"user": self.username, "password": self.password}
        headers = {"Content-type": "application/json"}
        response = requests.post(url, data=json.dumps(payload), headers=headers, verify=False)
        if response.status_code == 200:
            data = response.json()
            self.user_id, self.auth_token = data["data"]["userId"], data["data"]["authToken"]
        else:
            print("Login failed!")

    def get_group_id(self, group_name):
        url = f"https://{self.base_url}/api/v1/groups.list"
        headers = {
            "X-Auth-Token": self.auth_token,
            "X-User-Id": self.user_id
        }
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            data = response.json()
            groups = data["groups"]
            for group in groups:
                if group["name"] == group_name:
                    print(f"Group ID of {group_name}: {group['_id']}")
                    return group["_id"]
            print(f"No group found with the name {group_name}")
        else:
            print("Failed to get groups!")

    def get_latest_messages_from_group(self, room_id, count=10):
        url = f"https://{self.base_url}/api/v1/groups.messages?roomId={room_id}&count={count}"
        headers = {
            "X-Auth-Token": self.auth_token,
            "X-User-Id": self.user_id
        }
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            data = response.json()
            messages = data["messages"]
            if messages:
                latest_messages = [message['msg'] for message in messages]
                print(f"Latest messages: {latest_messages}")
                return latest_messages
            else:
                print("No messages in this group!")
                return []
        else:
            print("Failed to get messages!", response.content)
            return []

    def send_message_to_group(self, room_id, message):
        url = f"https://{self.base_url}/api/v1/chat.postMessage"
        payload = {"roomId": room_id, "text": message}
        headers = {
            "Content-type": "application/json",
            "X-Auth-Token": self.auth_token,
            "X-User-Id": self.user_id
        }
        response = requests.post(url, data=json.dumps(payload), headers=headers, verify=False)
        if response.status_code == 200:
            print("Message sent!")
        else:
            print("Failed to send message!")
