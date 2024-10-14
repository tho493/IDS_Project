import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import os
from dotenv import load_dotenv
dir_path = os.path.dirname(os.path.realpath(__file__))
dotenv_path = os.path.join(dir_path, '.env')
load_dotenv(dotenv_path)

from_email = os.environ.get("EMAIL")
password = os.environ.get("PASSWORD_EMAIL")

def send_email_with_image(to_email, image_path, message_body):
    # Cấu hình SMTP
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(from_email, password)

    # Tạo email
    message = MIMEMultipart()
    message["From"] = from_email
    message["To"] = to_email
    message["Subject"] = "Security Alert"

    message.attach(MIMEText(message_body, "plain"))

    # Đọc và đính kèm ảnh
    with open(image_path, "rb") as img_file:
        img = MIMEImage(img_file.read())
        message.attach(img)

    # Gửi email
    server.sendmail(from_email, to_email, message.as_string())
    server.quit()