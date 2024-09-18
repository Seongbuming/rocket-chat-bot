import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from rocket_chat import RocketChat

class ServerStatus:
    def __init__(self, chat_api: RocketChat, status_file="server_status.txt"):
        self.chat_api = chat_api
        self.url = f'https://{chat_api.base_url}'
        self.status_file = status_file
        self.previous_status = None
        self.session = self.create_retry_session()

    def load_previous_status(self):
        """이전 상태를 파일에서 로드"""
        if os.path.exists(self.status_file):
            with open(self.status_file, "r") as f:
                self.previous_status = f.read().strip()
        else:
            self.previous_status = None

    def save_current_status(self, status):
        """현재 상태를 파일에 저장"""
        with open(self.status_file, "w") as f:
            f.write(status)

    def check_status(self):
        """서버 상태를 체크"""
        try:
            response = self.session.get(self.url, timeout=10)
            if response.status_code == 200:
                return "up"
            else:
                return "down"
        except requests.exceptions.RequestException as e:
            print(f"Error checking server status: {e}")
            return "down"

    def create_retry_session(self, retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504)):
        """재시도 로직이 포함된 세션 생성"""
        session = requests.Session()
        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session

    def send_status_change(self, group_id):
        """상태 변화를 감지하고 메시지 전송"""
        self.load_previous_status()
        current_status = self.check_status()

        if self.previous_status != current_status:
            # 상태가 변하면 메시지 전송
            if current_status == "up":
                message = "VISLAB Rocket.Chat is back up!"
                self.chat_api.send_message_to_group(group_id, message)
                print(message)
            else:
                message = "VISLAB Rocket.Chat is down!"
                print(message)

            # 새로운 상태 저장
            self.save_current_status(current_status)
        else:
            pass
