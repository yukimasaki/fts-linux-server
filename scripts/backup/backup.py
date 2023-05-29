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
    backup_source_path = os.environ['BACKUP_SOURCE_PATH']
    backup_destination_path = os.environ['BACKUP_DESTINATION_PATH']

    try:
        # バックアップを保存する上限の日数
        max_backup_saved = 7

        # 除外リストを指定
        exclude_list = f'{os.path.dirname(__file__)}/exclude.list'
        print(exclude_list)

        # 今日の日付を取得
        raw_today = datetime.datetime.now()
        today = raw_today.strftime('%Y-%m-%d')

        # 昨日の日付を取得
        raw_yesterday = raw_today - datetime.timedelta(days=1)
        yesterday = raw_yesterday.strftime('%Y-%m-%d')

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
                --exclude-from={exclude_list} \
                --link-dest={yesterday_dir} \
                {backup_source_path} \
                {today_dir}
                '''
            subprocess.run(cmd.split())
            d = remove_old_backups(max_backup_saved, backup_destination_path)
            if d == None:
                body = f'\n削除されたフォルダはありません。'
            else:
                deleted_dirs = '\n'.join(d)
                body = f'\n以下のフォルダが削除されました。\n{deleted_dirs}'
            result = {'status': '成功', 'subject': 'バックアップが正常に終了しました', 'body': body}
        else:
            result = {'status': '中断', 'subject': 'バックアップは既に存在します', 'body': ''}
    except Exception as ex:
        result = {'status': '失敗', 'subject': f'予期しないエラーによりバックアップが失敗しました', 'body': ex}
    finally:
        subject = f'[{customer}][{result["status"]}]{result["subject"]}'
        message = f'ステータス: {result["status"]}\n結果: {result["subject"]}\n{result["body"]}'
        mime = send_email.create_mime_text(from_email, to_email, message, subject)
        send_email.send_email(mime)

def remove_old_backups(max_backup_saved, backup_destination_path):
    dirs = []
    for f in os.listdir(backup_destination_path):
        if os.path.isdir(os.path.join(backup_destination_path, f)):
            dirs.append(f)

    if len(dirs) < max_backup_saved:
        dirs_to_remove = None
        return dirs_to_remove
    else:
        dirs.sort(reverse=True)
        dirs_to_remove = dirs[max_backup_saved:]
        for dir_name in dirs_to_remove:
            dir_path = os.path.join(backup_destination_path, dir_name)
            if os.path.isdir(dir_path):
                # shutil.rmtreeだと権限が足りず削除できないディレクトリがあったのでsubprocessでrm -rfを実行している
                cmd = f'sudo rm -rf {dir_path}'
                subprocess.run(cmd.split())
        return dirs_to_remove

#main()