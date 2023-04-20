#!/opt/example/bin/python3
import datetime
import os
import subprocess
from dotenv import load_dotenv
from common import send_email

def main():
    load_dotenv()
    customer = os.environ['CUSTOMER']
    from_email = os.environ['FROM_EMAIL']
    to_email = os.environ['TO_EMAIL']

    try:
        # 今日の日付を取得
        raw_today = datetime.datetime.now()
        today = raw_today.strftime('%Y-%m-%d')

        # 昨日の日付を取得
        raw_yesterday = raw_today - datetime.timedelta(days=1)
        yesterday = raw_yesterday.strftime('%Y-%m-%d')

        # バックアップ先を指定
        backup_destination_path = '/mnt/storage/backup'

        # バックアップ先が存在しない場合、フォルダを作成する
        is_exist = os.path.isdir(backup_destination_path)
        if not is_exist:
            os.makedirs(backup_destination_path)

        # 日付毎のフォルダが存在しない場合、フォルダを作成しバックアップを実行する
        today_dir = f'{backup_destination_path}/snapshot_{today}'
        yesterday_dir = f'{backup_destination_path}/snapshot_{yesterday}'

        is_exist = os.path.isdir(today_dir)
        if not is_exist:
            os.makedirs(today_dir)
            cmd = f'''
                sudo rsync -a -ADHRSX -vi --delete --force --stats --delete-excluded \
                --exclude-from=exclude.list \
                --link-dest={yesterday_dir} \
                / \
                {today_dir}
                '''
            subprocess.run(cmd.split())
            result = {'status': '成功', 'subject': 'バックアップが正常に終了しました', 'body': ''}
        else:
            result = {'status': '中断', 'subject': 'バックアップは既に存在します', 'body': ''}
    except Exception as ex:
        result = {'status': '失敗', 'subject': f'予期しないエラーによりバックアップが失敗しました', 'body': ex}
    finally:
        subject = f'[{customer}][{result["status"]}]{result["subject"]}'
        message = f'ステータス: {result["status"]}\n結果: {result["subject"]}\nメッセージ: {result["body"]}'
        mime = send_email.create_mime_text(from_email, to_email, message, subject)
        send_email.send_email(mime)