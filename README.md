# 環境
```
OS: Ubuntu Server 22.04 LTS
Python: Python 3.10.6
```

# ディレクトリ構成
```
fts-linux-server
├── scripts
│   ├── backup
│   │   ├── backup.py
│   │   └── scheduler.py
│   ├── common
│   │   └── send_email.py
│   └── ngrok
│       ├── launch_ngrok.py
│       └── observer.py
├── services
│   ├── mybackup.service
│   └── ngrok.service
└── pyproject.toml
```
- `scripts` ... 各種のPythonスクリプトを配置しています。
    - `backup` ... 自動バックアップスクリプトを格納しています。
    - `common` ... 他のファイルから使いまわすためにモジュール化したスクリプトを格納しています。
    - `ngrok` ... ngrokの自動起動に関するスクリプトを格納しています。
- `services` ... 各種のSystemdユニットファイルを格納しています。所定のディレクトリにコピーして使います。
    - `mybackup.service` 自動バックアップに使います。
    - `ngrok.service` ngrokの自動起動に使います。
- `pyproject.toml` Poetryによる自作モジュールの管理に必要なファイルです。

# 使い方
- スクリプトの実行にはPoetryが必要です。
- インストールしていない場合は[仮想環境を構築する](#仮想環境を構築する)を参照してください。
- ngrokをインストールしていない場合は[ngrokをインストールする](#ngrokをインストールする)を参照してください。
- 自動バックアップの詳細は[自動バックアップ詳細](#自動バックアップ詳細)を参照してください。

ユーザーディレクトリで`git clone`します。
```bash
git clone https://github.com/yukimasaki/fts-linux-server.git
```

クローンしたリポジトリを`/opt/`に移動します。
```bash
sudo mv fts-linux-server/ /opt/
```

一括でパーミッションを変更します。
```bash
cd /opt/fts-linux-server
find ./ -name \*.py | xargs chmod 755
```

依存関係をインストールします。
```bash
source /opt/example/bin/activate
poetry install
deactivate
```

ユニットファイルを所定のディレクトリに移動します。
```bash
sudo mv services/mybackup.service /usr/lib/systemd/system/
sudo mv services/ngrok.service /usr/lib/systemd/system/
```

メール通知設定をします。
ログイン情報などは`.env`ファイルに記述します。
```bash
nano .env
```

以下の通り変更します。  
`CUSTOMER`の内容はメール件名に表示されます。  
例: `[hogehoge] ngrokの常駐が開始しました`
```.env
CUSTOMER=hogehoge
FROM_EMAIL=from@example.com
TO_EMAIL=to@example.com
EMAIL_USER=from@example.com
EMAIL_PASSWORD=fugafuga
SMTP_SERVER=smtp.example.com
```

ngrokのコンフィグを必要に応じて編集します。
以下は、CockpitとSSHの2つのトンネルを作成するための書式です。
```yaml:/root/.config/ngrok/ngrok.yml
version: "2"
authtoken: XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

tunnels:
  cockpit:
    proto: tcp
    addr: 9090
  ssh:
    proto: tcp
    addr: 22
```

サービスを起動します。
```bash
sudo systemctl daemon-reload
sudo systemctl start mybackup.service
sudo systemctl start ngrok.service
```

エラーが出ていないか確認します。
```bash
sudo systemctl status mybackup.service
sudo systemctl status ngrok.service
# Active: active (running)
```

サービスを永続化します。
```bash
sudo systemctl enable mybackup.service
sudo systemctl enable ngrok.service
```

ngrok.serviceが起動すると`TO_EMAIL`で指定したメールアドレスに通知が届きます。
通知メールには以下の情報が記載されています。
- 接続用アドレス
- 接続用ポート番号

# 仮想環境を構築する
Python3とPoetryをインストールします。  
Ubuntu Server 22.04には、システムが使用するPythonがデフォルトでインストールされていますが、環境汚染を防ぐため仮想環境を別途準備します。

## Python3をインストールする
venvモジュールをインストールします。
```bash
sudo apt install -y python3-venv
```

`/opt`に仮想環境を作成します。
```bash
sudo python3 -m venv example
```

作成した仮想環境の所有権を変更します。
```bash
sudo chown -R $USER:$USER example/
```

仮想環境の構築が完了しました。  
実行パスは`/opt/example/bin/python3`となります。  

以下のコマンドで仮想環境に入ることができます。
```bash
source /opt/example/bin/activate
```

仮想環境から出るには以下のコマンドを打ちます。
```bash
deactivate
```

## Poetryをインストールする
自作モジュールを管理するためのツールを導入します。

まずは仮想環境に入ります。
```bash
source /opt/example/bin/activate
```

Poetryをインストールします。
```bash
pip install poetry
```

# ngrokをインストールする
[公式サイト](https://ngrok.com)でユーザー登録をします。

実行ファイルをダウンロードします。
```bash
wget https://bin.equinox.io/c/XXXXXX/ngrok-v3-stable-linux-amd64.tgz
```

圧縮ファイルを解凍します。
```bash
tar zxf ngrok-v3-stable-linux-amd64.tgz
```

実行ファイルのパスを通します。
```bash
sudo mv ngrok /usr/local/bin
```

AuthTokenを登録します。
```bash
sudo ngrok config add-authtoken XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

# 自動バックアップ詳細
## 概要
自動バックアップは以下のファイルで構成されます。
- services/mybackup.service
- scripts/backup/scheduler.py
- scripts/backup/backup.py

## mybackup.service
所定のディレクトリに配置して使用します。  
サービス化することで不意のプロセス終了を防ぎます。
詳細は[使い方](#使い方)を参照してください。

## scheduler.py
スケジュールを有効化します。
デフォルトでは毎夜1時にバックアップを実行します。

## backup.py
メインのスクリプトファイルです。
バックアップ保存先や保持する世代数などはこのファイルで指定します。

### バックアップ対象の仮想マシンを指定する
```python
vms = [
    {'name': 'vm-ubuntu', 'disk': 'vda'},
    {'name': 'vm-win', 'disk': 'sda'}
]
```

`name`には仮想マシン名を、`disk`には仮想マシンのイメージファイル(*.qcow2)が存在するデバイス名を指定します。
以下のコマンドで確認できます。
```bash
sudo virsh list # 仮想マシン名を確認
sudo virsh domblklist <vm_name> # デバイス名を確認
```