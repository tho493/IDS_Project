import requests

def send_message_with_photo(message, photo_path, chat_id, token):
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