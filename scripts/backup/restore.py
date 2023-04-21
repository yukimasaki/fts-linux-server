#!/opt/example/bin/python3
import os
import subprocess
from dotenv import load_dotenv
from common import send_email

try:
    load_dotenv()
    customer = os.environ['CUSTOMER']
    from_email = os.environ['FROM_EMAIL']
    to_email = os.environ['TO_EMAIL']

    # リストア先を指定
    restore_destination_path = '/'

    # リストア元を指定
    restore_source_path = '/mnt/storage/backup/snapshot_2023-04-21'

    # 除外リストを指定
    exclude_list = f'{os.path.dirname(__file__)}/exclude.list'

    # 復元先の存在を確認
    is_exist = os.path.isdir(restore_destination_path)
    if not is_exist:
        # 存在しない場合は、メッセージをresultへ格納し処理を中断
        body = f'\nリストア先「{restore_destination_path}」が存在しません'
        result = {'status': '中断', 'subject': 'リストア先のディレクトリが存在しません', 'body': body}
    else:
        # 存在する場合は処理を続行し、リストア元の存在を確認
        is_exist = os.path.isdir(restore_source_path)
        if not is_exist:
            # 存在しない場合は、メッセージをresultへ格納し処理を中断
            body = f'\nリストア元「{restore_source_path}」が存在しません'
            result = {'status': '中断', 'subject': 'リストア元のディレクトリが存在しません', 'body': body}
        else:
            # 存在する場合は処理を続行し、リストアを実行
            cmd = f'''
                sudo rsync -a -ADHSX -vi --delete --force --stats \
                --exclude-from={exclude_list} \
                {restore_source_path} \
                {restore_destination_path}
                '''
            subprocess.run(cmd.split())

            # 成功を知らせるメッセージをresultへ格納
            body = f'\nリストア元:{restore_source_path}\nリストア先:{restore_destination_path}'
            result = {'status': '成功', 'subject': 'バックアップが正常に終了しました', 'body': body}
# 例外処理: エラー内容をresultへ格納
except Exception as ex:
    result = {'status': '失敗', 'subject': f'予期しないエラーによりバックアップが失敗しました', 'body': ex}
# 共通処理: メールを送信する
finally:
    subject = f'[{customer}][{result["status"]}]{result["subject"]}'
    message = f'ステータス: {result["status"]}\n結果: {result["subject"]}\n{result["body"]}'
    mime = send_email.create_mime_text(from_email, to_email, message, subject)
    send_email.send_email(mime)