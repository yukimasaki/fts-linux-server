#!/opt/example/bin/python3
from dotenv import load_dotenv
import os
import subprocess

autossh_username = os.environ['AUTOSSH_USERNAME']
autossh_domain = os.environ['AUTOSSH_DOMAIN']
autossh_remote_port = os.environ['AUTOSSH_REMOTE_PORT']
autossh_local = os.environ['AUTOSSH_LOCAL']

cmd = f'autossh -fN {autossh_username}@{autossh_domain} -p 55555 -R {autossh_remote_port}:{autossh_local}'

subprocess.run(cmd.split())