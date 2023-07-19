import requests
import urllib3
import json

class RocketChat:
    def __init__(self, base_url, username, password, debug=False):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.debug = debug

        self.auth_token = None
        self.user_id = None

        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.login()

    def request(self, method, endpoint, payload=None) -> requests.Response:
        url = f"https://{self.base_url}{endpoint}"
        headers = {
            "Content-type": "application/json",
            "X-Auth-Token": self.auth_token,
            "X-User-Id": self.user_id
        }
        if payload:
            response = requests.request(method, url, data=json.dumps(payload), headers=headers, verify=False)
        else:
            response = requests.request(method, url, headers=headers, verify=False)
        return response

    def login(self):
        payload = {"user": self.username, "password": self.password}
        response = self.request("POST", "/api/v1/login", payload)
        if response.status_code == 200:
            data = response.json()
            self.user_id, self.auth_token = data["data"]["userId"], data["data"]["authToken"]
        else:
            print("Login failed!")

    def get_group_id(self, group_name):
        response = self.request("GET", "/api/v1/groups.list")
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
        response = self.request("GET", f"/api/v1/groups.messages?roomId={room_id}&count={count}")
        if response.status_code == 200:
            data = response.json()
            messages = data["messages"]
            if messages:
                return messages
            else:
                print("No messages in this group!")
                return []
        else:
            print("Failed to get messages!", response.content)
            return []

    def send_message_to_group(self, group_id, message):
        payload = {
            "roomId": group_id,
            "text": message
        }
        if self.debug:
            print("send", payload)
        else:
            response = self.request("POST", "/api/v1/chat.postMessage", payload)
            if response.status_code == 200:
                print("Message sent!")
            else:
                print("Failed to send message!")
        
    def update_message_from_group(self, group_id, message_id, message):
        payload = {
            "roomId": group_id,
            "msgId": message_id,
            "text": message
        }
        if self.debug:
            print("update", payload)
        else:
            response = self.request("POST", "/api/v1/chat.update", payload)
            if response.status_code == 200:
                print("Message updated!")
            else:
                print("Failed to update message!")
