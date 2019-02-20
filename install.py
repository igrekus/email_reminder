# -*- coding: UTF-8 -*-
import subprocess

subprocess.run(['pyinstaller', '--onedir', 'reminder.py', '--clean'])
