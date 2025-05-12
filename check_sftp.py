#!/usr/bin/env python3

# Brent Hartley
# GNU Public License V3

import paramiko
import datetime
import smtplib
import stat
import os
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

def check_sftp_files():
    hostname = os.getenv('SFTP_HOST')
    username = os.getenv('SFTP_USER')
    password = os.getenv('SFTP_PASS')
    port = int(os.getenv('SFTP_PORT', 22))
    folder_path = os.getenv('SFTP_FOLDER')

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, port=port, username=username, password=password)
    sftp = ssh.open_sftp()

    now = datetime.datetime.now()
    old_files = []

    try:
        for file_attr in sftp.listdir_attr(folder_path):
            if not stat.S_ISDIR(file_attr.st_mode):
                file_path = f"{folder_path}/{file_attr.filename}"
                file_time = datetime.datetime.fromtimestamp(file_attr.st_mtime)
                alert_age = int(os.getenv('ALERT_AGE_HOURS', 6))
                if (now - file_time).total_seconds() > alert_age * 3600:
                    old_files.append(file_path)
    except IOError as e:
        print(f"Error: Unable to access the folder {folder_path}. {str(e)}")

    sftp.close()
    ssh.close()

    return old_files

def send_email_alert(old_files):
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = int(os.getenv('SMTP_PORT', 587))
    sender_email = os.getenv('SENDER_EMAIL')
    sender_password = os.getenv('SENDER_EMAIL_PASSWORD')
    receiver_email = os.getenv('RECEIVER_EMAIL')

    subject = "SFTP File Alert"
    body = "The following files are older than the allowed threshold:\n\n" + "\n".join(old_files)
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = receiver_email

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)

if __name__ == "__main__":
    old_files = check_sftp_files()
    if old_files:
        send_email_alert(old_files)
