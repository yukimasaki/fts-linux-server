#!/opt/example/bin/python3
# このスクリプトはngrok起動用スクリプトに先駆けて非同期的に起動し、
# ngrokのサービス開始=ログファイルの変更を監視する。

from dotenv import load_dotenv

import time
import os
import re
from common import send_email

# .envファイルの内容を読み込む
load_dotenv()

log_path = f'/opt/fts-linux-server/scripts/ngrok/ngrok.log'

# ５秒待機すればログファイルの書き込みが終わるはず
time.sleep(5)

# ログファイルに内容が出力されたはずなので、メインの処理を開始する。
with open(log_path, 'r') as f:
    rows = f.read().split('\n')

# ログファイルからアクセス用アドレスを正規表現で抽出する
regex = 'url=tcp://(.+ngrok\.io):(\d{5})'
for row in rows:
    match_object = re.search(regex, row)
    if match_object:
        ngrok_host = match_object.group(1) # ホスト名
        ngrok_port = match_object.group(2) # ポート番号

# 抽出した情報をメールで通知する
customer = os.environ['CUSTOMER']
from_email = os.environ['FROM_EMAIL']
to_email = os.environ['TO_EMAIL']
subject = f'[{customer}] ngrokの常駐が開始しました'
message = f'ngrokの常駐が開始しました。\n\nホスト: {ngrok_host}\nポート番号: {ngrok_port}'

mime = send_email.create_mime_text(from_email, to_email, message, subject)
send_email.send_email(mime)