import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage 

def send_email_with_image(to_email, image_path, message_body, from_email, password):
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