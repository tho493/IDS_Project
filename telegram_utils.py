# import telebot  # pip install pyTelegramBotAPI
import requests
import os
from dotenv import load_dotenv
dir_path = os.path.dirname(os.path.realpath(__file__))
dotenv_path = os.path.join(dir_path, '.env')
load_dotenv(dotenv_path)

chat_id = os.environ.get("TELEGRAM_TOKEN")
token = os.environ.get("CHAT_ID")

def send_message_with_photo(message, photo_path):
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    files = {'photo': open(photo_path, 'rb')}
    data = {
        'chat_id': chat_id,
        'caption': message
    }
    response = requests.post(url, files=files, data=data)
    if response.status_code == 200:
        print(f"Đã gửi cảnh báo")
    else:
        print(f"Lỗi : {response.text}")