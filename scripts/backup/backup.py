#!/opt/example/bin/python3
import datetime
import os
from dotenv import load_dotenv
from common import send_email
import xml.etree.ElementTree as ET
import time
import subprocess

def main():
    load_dotenv()
    customer = os.environ['CUSTOMER']
    from_email = os.environ['FROM_EMAIL']
    to_email = os.environ['TO_EMAIL']

    # バックアップ対象の仮想マシン名を配列で指定
    vms = [
        {'name': 'test-ubuntu', 'disk': 'vda'},
        {'name': 'test-win', 'disk': 'sda'}
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
            backup_image_path = f'{backup_destination_path}/{vm["name"]}_{today}.qcow2'
            # 当日のバックアップイメージファイルが既に存在する場合は処理を中断
            if os.path.isfile(backup_image_path):
                result = {'vm': vm["name"], 'status': '中断', 'subject': 'バックアップは既に存在します', 'body': ''}
            # 存在しない場合は処理を続行
            else:               
                # xmlファイルを作成
                xml_file_name = f'{vm["name"]}_{today}.xml'
                xml_file_path = create_backup_xml(vm, backup_destination_path, xml_file_name, backup_image_path)

                # バックアップを開始
                begin_backup = f'sudo virsh backup-begin {vm["name"]} --backupxml {xml_file_path}'
                subprocess.run(begin_backup.split())

                # 進捗の確認を開始
                # 「Job type: Unbounded」である間は処理を継続し、それ以外の結果の場合は次の処理へ移行する
                job_running = True
                while job_running:
                    is_working = f'sudo virsh domjobinfo {vm["name"]}'
                    result = subprocess.run(is_working.split(), capture_output=True, text=True)
                    job_running = 'Job type:         Unbounded' in result.stdout                    
                    if not job_running: break
                    time.sleep(10)

                # 「Job type: Completed」の場合は処理を正常終了し、それ以外の結果の場合は例外をスローする
                is_completed = f'sudo virsh domjobinfo {vm["name"]} --completed'
                result = subprocess.run(is_completed.split(), capture_output=True, text=True)

                if 'Job type:         Completed' in result.stdout:
                    result = {'vm': vm["name"], 'status': '成功', 'subject': 'バックアップが正常に終了しました', 'body': 'body'}
                else:
                    raise Exception

        except Exception as ex:
            result = {'vm': vm["name"], 'status': '失敗', 'subject': f'予期しないエラーによりバックアップが失敗しました', 'body': ex}            
            
        finally:
            subject = f'[{customer}][{result["vm"]}][{result["status"]}]{result["subject"]}'
            message = f'ステータス: {result["status"]}\n結果: {result["subject"]}\n{result["body"]}'

            # mime = send_email.create_mime_text(from_email, to_email, message, subject)
            # # send_email.send_email(mime)
            print(result)

def create_backup_xml(vm, backup_destination_path, xml_file_name, backup_image_path):
    # 親要素「domainbackup」を作成
    domainbackup = ET.Element("domainbackup")
    
    # 子要素「disks」を作成しdomainbackupに追加する
    disks = ET.Element("disks")
    domainbackup.append(disks)
    
    # 孫要素「disk」を作成し属性値を設定する
    disk = ET.Element("disk")
    disk.set("name", vm["disk"])
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
    xml_file_path = os.path.join(backup_destination_path, xml_file_name)
    tree = ET.ElementTree(domainbackup)
    tree.write(xml_file_path)

    return xml_file_path

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