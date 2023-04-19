#!/opt/example/bin/python3
from dotenv import load_dotenv
import os
import pathlib
import subprocess

# .envファイルの内容を読み込む
load_dotenv()

log_path = f'/opt/fts-linux-server/scripts/ngrok/ngrok.log'

is_exist = os.path.isfile(log_path)
if not is_exist:
    # ログファイルが存在しない場合、空のログファイルを作成する
    not_exist = pathlib.Path(log_path)
    not_exist.touch()
else:
    # ログファイルが存在する場合、内容を消去する
    log_file = open(log_path, 'r+')
    log_file.truncate(0)
    log_file.close()

# ngrok起動用スクリプトに先駆けて、非同期的にログ監視スクリプトを起動しておく
cmd = f'/opt/fts-linux-server/scripts/ngrok/observer.py'
subprocess.Popen(cmd.split())

# ngrokを起動時にアクセス用アドレス等をログファイルに出力する
port = os.environ['NGROK_PORT']
config_path = '/root/.config/ngrok/ngrok.yml'

cmd = f'ngrok tcp {port} --log={log_path} --config={config_path}'
subprocess.run(cmd.split())