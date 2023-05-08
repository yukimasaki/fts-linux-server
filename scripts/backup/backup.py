#!/opt/example/bin/python3
import datetime
import os
from dotenv import load_dotenv
from common import send_email
import xml.etree.ElementTree as ET
import time
import subprocess
import re

class LowDiskSpaceError(Exception):
    pass

def main():
    load_dotenv()
    customer = os.environ['CUSTOMER']
    from_email = os.environ['FROM_EMAIL']
    to_email = os.environ['TO_EMAIL']

    # 当日の日付を取得
    now = datetime.datetime.now()
    today = now.strftime('%Y-%m-%d')

    # バックアップ対象の仮想マシン名を配列で指定
    vms = [
        {'name': 'test-ubuntu', 'disk': 'vda'},
        {'name': 'test-win', 'disk': 'sda'}
    ]
    
    # バックアップ先の外部ストレージを指定
    external_storage = '/mnt/storage'

    # バックアップ保持数
    max_backup_generations = 7

    # 以下の閾値を超過した場合は容量不足の警告を出す
    max_backup_space = 0.8 # 80%
    
    for vm in vms:
        try:
            # バックアップ先のディレクトリを指定
            backup_destination_path = f'{external_storage}/backup/{vm["name"]}'
            # 存在しない場合は作成する
            if not os.path.isdir(backup_destination_path):
                os.makedirs(backup_destination_path)

            # バックアップ先の空き容量を確認
            used_numeric = available_space(external_storage)
            if used_numeric > max_backup_space:
                raise LowDiskSpaceError('ディスク容量不足のため、不要なバックアップを削除してバックアップ保持数を調整してください。')
            
            # 開始を知らせるメールを送信
            result = {'vm': vm["name"], 'status': '開始', 'subject': 'バックアップを開始しました', 'body': ''}
            subject = f'[{customer}][{result["vm"]}][{result["status"]}]{result["subject"]}'
            message = f'ステータス: {result["status"]}\n結果: {result["subject"]}\n{result["body"]}'

            mime = send_email.create_mime_text(from_email, to_email, message, subject)
            send_email.send_email(mime)
            print(result)

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
                    job_result = subprocess.run(is_working.split(), capture_output=True, text=True)
                    job_running = is_matched(r'Job type\:\s{1,}Unbounded', job_result.stdout)
                    if not job_running: break
                    time.sleep(10)

                # 「Job type: Completed」の場合は処理を正常終了し、それ以外の結果の場合はジョブを中断し例外をスローする
                is_completed = f'sudo virsh domjobinfo {vm["name"]} --completed'
                job_result = subprocess.run(is_completed.split(), capture_output=True, text=True)

                if is_matched(r'Job type\:\s{1,}Completed', job_result.stdout):
                    # 古いバックアップを削除する処理を実装する

                    result = {'vm': vm["name"], 'status': '成功', 'subject': 'バックアップが正常に終了しました', 'body': ''}
                else:
                    abort_job = f'sudo virsh domjobabort {vm["name"]}'
                    subprocess.run(abort_job.split())
                    raise Exception

        except LowDiskSpaceError as lds:
            result = {'vm': vm["name"], 'status': '失敗', 'subject': f'バックアップ先のディスク容量が不足しています', 'body': lds}

        except Exception as ex:
            result = {'vm': vm["name"], 'status': '失敗', 'subject': f'予期しないエラーによりバックアップが失敗しました', 'body': ex}
            
        finally:
            subject = f'[{customer}][{result["vm"]}][{result["status"]}]{result["subject"]}'
            message = f'ステータス: {result["status"]}\n結果: {result["subject"]}\n{result["body"]}'

            mime = send_email.create_mime_text(from_email, to_email, message, subject)
            send_email.send_email(mime)
            print(result)

def is_matched(regex, string):
    if re.match(regex, string):
        return True
    else:
        return False

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

def available_space(external_storage):
    # コマンドを実行して、標準出力を取得する
    cmd = f'df -h {external_storage}'
    dir_info = subprocess.run(cmd.split(), stdout=subprocess.PIPE)

    # 標準出力を文字列に変換する
    output = dir_info.stdout.decode('utf-8')

    # 出力から「Use%」の値を抽出する
    for line in output.split('\n'):
        if external_storage in line:
            used_percentage = line.split()[4]
            used_numeric = re.sub(r'\D', '', used_percentage)
            used_numeric = int(used_numeric) * 0.01
            break

    return used_numeric

# デバッグ時のみmain関数を呼び出す
# 本番運用時はコメントアウトすること
main()