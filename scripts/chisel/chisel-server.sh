#!/bin/bash
# .envを読み込む ###########################
source ./.env

# 変数を定義 ###########################
log_dir="/var/log/chisel"
log_file="$log_dir/server.log"
search_string="Listening on https://0.0.0.0:443"

# 関数を定義 ###########################
# サーバーが起動中か否かを判定する関数
listening() {
    if grep -q "$search_string" "$log_file"; then
        echo "True"
    else
        echo "False"
    fi
}

# メイン処理 ###########################
# ログディレクトリが存在しない場合は作成する
if [ ! -d "$log_dir" ]; then
    mkdir "$log_dir"
fi

# chiselをバックグラウンドで起動する
nohup chisel server --reverse --port 443 --tls-domain "$TLS_DOMAIN" > "$log_file" &

# サーバーの起動状態を判定
if listening; then
    echo "chiselが起動中です"
else
    echo "chiselの起動に失敗しました"
fi