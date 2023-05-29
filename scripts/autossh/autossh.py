#!/opt/example/bin/python3
from dotenv import load_dotenv
import os
import subprocess

load_dotenv()
autossh_host = os.environ['AUTOSSH_HOST']


cmd = f'autossh -fN {autossh_host}'

subprocess.run(cmd.split())