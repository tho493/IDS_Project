# import telebot  # pip install pyTelegramBotAPI
import requests


chat_id = "1170615246"
token = "6407537309:AAF_PAtoN5mgYBFN3HVmOmYLksMDgbQoQXA"


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

# bot = telebot.TeleBot(token)


# def send_message_with_photo(message, photo_path):
#     photo = open(photo_path, 'rb')
#     bot.send_photo(chat_id, photo, caption=message)
