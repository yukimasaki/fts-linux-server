# 環境
```
OS: Ubuntu Server 22.04 LTS
Python: Python 3.10.6
```

# ディレクトリ構成
```
fts-linux-server
├── scripts
│   ├── common
│   │   └── send_email.py
│   └── ngrok
│       ├── launch_ngrok.py
│       └── observer.py
├── ngrok.service
└── pyproject.toml
```
- `scripts` ... 種々のPythonスクリプトを配置しています。  
    - `common` ... 他のファイルから使いまわすためにモジュール化したスクリプトを格納しています。  
    - `ngrok` ... ngrokの自動起動に関するスクリプトを格納しています。  
- `ngrok.service` Systemdのユニットファイルです。所定のディレクトリにコピーして使います。
- `pyproject.toml` Poetryによる自作モジュールの管理に必要なファイルです。

# 使い方
- スクリプトの実行にはPoetryが必要です。
- インストールがまだの場合は[仮想環境を構築する](#仮想環境を構築する)を参照してください。
- ngrokがインストールされていない場合は[ngrokをインストールする](#ngrokをインストールする)を参照してください。

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

ngrok.serviceを所定のディレクトリに移動します。
```bash
sudo mv ngrok.service /usr/lib/systemd/system/
```

メール通知設定をします。
ログイン情報などは`.env`ファイルに記述します。
```bash
nano .env
```

下記の通り変更します。  
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

ngrokのサービスを有効化(デーモン化)します。
```bash
sudo systemctl daemon-reload
sudo systemctl start ngrok.service
```

エラーが出ていないか確認します。
```bash
sudo systemctl status ngrok.service
# Active: active (running)
```

サービスを永続化します。
```bash
sudo systemctl enable ngrok.service
```

サービスが起動すると`TO_EMAIL`で指定したメールアドレスに通知が届きます。
通知メールには以下の情報が記載されています。
- 接続用アドレス
- 接続用ポート番号

# 仮想環境を構築する
Python3とPoetryをインストールします。  
Ubuntu Server 22.04には、システムが使用するPythonがデフォルトでインストールされていますが、環境汚染を防ぐため仮想環境を別途準備します。

## Python3のインストール
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

## Poetryのインストール
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
ngrok config add-authtoken XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```