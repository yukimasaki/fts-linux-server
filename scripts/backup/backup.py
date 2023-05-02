#!/opt/example/bin/python3
import datetime
import os
from dotenv import load_dotenv
from common import send_email
import xml.etree.ElementTree as ET

def main():
    load_dotenv()
    customer = os.environ['CUSTOMER']
    from_email = os.environ['FROM_EMAIL']
    to_email = os.environ['TO_EMAIL']

    # バックアップ対象の仮想マシン名を配列で指定
    vms = [
        'test-ubuntu'
    ]
    
    # バックアップ先を指定
    backup_destination_path = '/mnt/storage/backup'

    # 存在しない場合は作成しておく
    if not os.path.isdir(backup_destination_path):
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
                xml_file_name = f'{vm}_{today}.xml'
                create_backup_xml(backup_destination_path, xml_file_name, backup_image_path)

                # バックアップを開始                    

                # 進捗を確認

                # 完了したら処理を終了
                result = {'vm': vm, 'status': '成功', 'subject': 'バックアップが正常に終了しました', 'body': 'body'}
        except Exception as ex:
            result = {'vm': vm, 'status': '失敗', 'subject': f'予期しないエラーによりバックアップが失敗しました', 'body': ex}            
        finally:
            subject = f'[{customer}][{result["vm"]}][{result["status"]}]{result["subject"]}'
            message = f'ステータス: {result["status"]}\n結果: {result["subject"]}\n{result["body"]}'

            mime = send_email.create_mime_text(from_email, to_email, message, subject)
            send_email.send_email(mime)

def create_backup_xml(backup_destination_path, xml_file_name, backup_image_path):
    # 親要素「domainbackup」を作成
    domainbackup = ET.Element("domainbackup")
    
    # 子要素「disks」を作成しdomainbackupに追加する
    disks = ET.Element("disks")
    domainbackup.append(disks)
    
    # 孫要素「disk」を作成し属性値を設定する
    disk = ET.Element("disk")
    disk.set("name", "vda")
    disk.set("backup", "yes")
    disk.set("type", "file")
    
    # 孫要素「target」を作成し属性値を設定する
    target = ET.Element("target")
    target.set("file", backup_image_path)
    disk.append(target)
    
    # 孫要素「driver」を作成し属性値を設定する
    driver = ET.Element("driver")
    driver.set("type", "qcow2")
    disk.append(driver)
    
    # 孫要素「disk」をdisksに追加する
    disks.append(disk)
    
    # 改行とインデントを挿入する
    indent(domainbackup)
    
    # XMLファイルを作成し内容を書き込む
    xml_file = os.path.join(backup_destination_path, xml_file_name)
    tree = ET.ElementTree(domainbackup)
    tree.write(xml_file)

def indent(elem, level=0):
    # 改行とインデント用の空白文字列を作成する
    newline = '\n' + level * '  '
    # 要素が子要素を持っている場合、再帰的に呼び出して改行とインデント用の空白文字列を追加する
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = newline + '  '
        if not elem.tail or not elem.tail.strip():
            elem.tail = newline
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = newline
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = newline

# デバッグ時のみmain関数を呼び出す
# 本番運用時はコメントアウトすること
main()