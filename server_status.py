import os
import requests
from rocket_chat import RocketChat

class ServerStatus:
    def __init__(self, rocket_chat: RocketChat, status_file="server_status.txt"):
        self.url = f'https://{rocket_chat.base_url}'
        self.status_file = status_file
        self.previous_status = None

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
            response = requests.get(self.url, timeout=5)
            if response.status_code == 200:
                return "up"
            else:
                return "down"
        except requests.exceptions.RequestException:
            return "down"

    def send_status_change(self):
        """상태 변화를 감지하고 메시지 전송"""
        self.load_previous_status()
        current_status = self.check_status()

        if self.previous_status != current_status:
            # 상태가 변하면 메시지 전송
            if current_status == "up":
                print(f"VISLAB Rocket.Chat is back up!")
            # else:
            #     print(f"VISLAB Rocket.Chat is down!")

            # 새로운 상태 저장
            self.save_current_status(current_status)
        else:
            pass

if __name__ == "__main__":
    # 체크할 웹사이트 URL
    checker = ServerStatus("https://vislab.sejong.ac.kr")
    checker.log_status_change()
