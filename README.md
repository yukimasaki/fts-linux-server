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
スクリプトの実行にはPoetryが必要です。
インストールがまだの場合は[仮想環境を構築する](#仮想環境を構築する)を参照してください。

ユーザーディレクトリで`git clone`します。
```bash
git clone https://github.com/yukimasaki/fts-linux-server.git
```

クローンしたリポジトリを`/opt`に移動します。
```bash
sudo mv fts-linux-server /opt/fts-linux-server
```

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