#!/opt/example/bin/python3
import datetime
import os
import subprocess
import pathlib
from dotenv import load_dotenv
from common import send_email

def main():
    load_dotenv()
    customer = os.environ['CUSTOMER']
    from_email = os.environ['FROM_EMAIL']
    to_email = os.environ['TO_EMAIL']

    try:
        # バックアップ対象の仮想マシン名を配列で指定
        vms = [
            'test-ubuntu'
        ]
        
        # バックアップ先を指定
        backup_destination_path = '/mnt/storage/backup'

        # 存在しない場合は作成しておく
        if os.path.isdir(backup_destination_path):
            os.makedirs(backup_destination_path)

        # バックアップ保持数
        max_backup = 7

        # 当日の日付を取得
        now = datetime.datetime.now()
        today = now.strftime('%Y-%m-%d')

        for vm in vms:
            try:
                backup_image_path = f'{backup_destination_path}/{vm}_{today}.qcow2'
                # 当日のバックアップイメージファイルが既に存在する場合は処理を中断
                if os.path.isdir(backup_image_path):
                    result = {'status': '中断', 'subject': 'バックアップは既に存在します', 'body': ''}
                # 存在しない場合は処理を続行
                else:
                    # xmlファイルを作成
                    xml_path = pathlib.Path(f'{backup_destination_path}/{vm}_{today}.xml')
                    xml_path.touch()

                    # バックアップを開始

                    # 進捗を確認

                    # 完了したら処理を終了
                    result = {'vm': vm, 'status': '成功', 'subject': 'バックアップが正常に終了しました', 'body': body}
            except Exception as ex:
                result = {'vm': vm, 'status': '失敗', 'subject': f'予期しないエラーによりバックアップが失敗しました', 'body': ex}            
            finally:
                subject = f'[{customer}][{result["vm"]}][{result["status"]}]{result["subject"]}'
                message = f'ステータス: {result["status"]}\n結果: {result["subject"]}\n{result["body"]}'

                mime = send_email.create_mime_text(from_email, to_email, message, subject)
                send_email.send_email(mime)