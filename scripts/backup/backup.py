#!/opt/example/bin/python3
import datetime
import os
import subprocess

try:
    # 今日の日付を取得
    raw_today = datetime.datetime.now()
    today = raw_today.strftime('%Y-%m-%d')

    # 昨日の日付を取得
    raw_yesterday = raw_today - datetime.timedelta(days=1)
    yesterday = raw_yesterday.strftime('%Y-%m-%d')

    # バックアップ先を指定
    backup_destination_path = '/mnt/storage/backup-test'

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
    else:
        raise Exception
except Exception as e:
    print('エラー:', e.args)

# バックアップ成功・失敗をメール通知