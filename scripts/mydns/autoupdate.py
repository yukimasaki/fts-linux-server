#!/opt/example/bin/python3

def main():
    import os
    from dotenv import load_dotenv
    import subprocess
    
    load_dotenv()
    mydns_user = os.environ['MYDNS_USER']
    mydns_password = os.environ['MYDNS_PASSWORD']

    cmd = f'curl https://ipv4.mydns.jp/login.html -u {mydns_user}:{mydns_password}'
    subprocess.run(cmd.split())