#!/opt/sh/bin/python3
from dotenv import load_dotenv
import os

import ssl
from smtplib import SMTP, SMTP_SSL
from email.mime.text import MIMEText
from email.utils import formatdate

# .envファイルの内容を読み込む
load_dotenv()

def create_mime_text(from_email, to_email, message, subject):
    msg = MIMEText(message, 'plain', 'utf-8')

    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg['Date'] = formatdate()

    return msg

def send_email(msg):
    email_user = os.environ['EMAIL_USER']
    email_password = os.environ['EMAIL_PASSWORD']

    host = os.environ['SMTP_SERVER']
    port = 465

    # サーバを指定する
    context = ssl.create_default_context()
    server = SMTP_SSL(host, port, context=context)

    # ログイン処理
    server.login(email_user, email_password)

    # メールを送信する
    server.send_message(msg)
    
    # 閉じる
    server.quit()