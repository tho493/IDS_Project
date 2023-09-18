import requests
from dotenv import load_dotenv
import os

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=dotenv_path)

chat_id = os.getenv("chat_id")
token = os.getenv("token")

def send_message_with_photo(message, photo_path):
    if(os.getenv("enable_send_telegram") == "0"):
        return print("Gửi tin nhắn tới telegram đang bị vô hiệu hóa")
    else:
        url = f"https://api.telegram.org/bot{token}/sendPhoto"
        files = {'photo': open(photo_path, 'rb')}
        data = {
            'chat_id': chat_id,
            'caption': message
        }
        response = requests.post(url, files=files, data=data)
        # response = requests.get(url, files=files, data=data)
        if response.status_code == 200:
            print("Tin nhắn và ảnh đã được gửi thành công!")
        else:
            print(f"Lỗi : {response.text}")

# send_message_with_photo("ALARM!!!!", dir_path + "/alert.png")
