import os
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import paramiko
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# SFTP configuration
SFTP_HOST = os.getenv("SFTP_HOST")
SFTP_PORT = int(os.getenv("SFTP_PORT", 22))
SFTP_USER = os.getenv("SFTP_USER")
SFTP_PASS = os.getenv("SFTP_PASS")
SFTP_FOLDER = os.getenv("SFTP_FOLDER")

# Email configuration
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_EMAIL_PASSWORD = os.getenv("SENDER_EMAIL_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")

# File alert configuration
ALERT_AGE_HOURS = int(os.getenv("ALERT_AGE_HOURS", 6))

# File to store alerted files
ALERTED_FILE_PATH = '/app/alerted_files.txt'

def get_older_files(sftp_client):
    """ Get files older than the configured ALERT_AGE_HOURS. """
    older_files = []
    current_time = time.time()

    # List files in the SFTP folder
    for filename in sftp_client.listdir_attr(SFTP_FOLDER):
        file_path = os.path.join(SFTP_FOLDER, filename.filename)
        file_time = sftp_client.stat(file_path).st_mtime
        file_age_hours = (current_time - file_time) / 3600

        if file_age_hours > ALERT_AGE_HOURS:
            older_files.append(filename.filename)

    return older_files

def send_email(subject, body):
    """ Send an email notification. """
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_EMAIL_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())

def check_sftp():
    """ Check SFTP folder for old files and send alerts. """
    # Connect to SFTP server
    transport = paramiko.Transport((SFTP_HOST, SFTP_PORT))
    transport.connect(username=SFTP_USER, password=SFTP_PASS)
    sftp_client = paramiko.SFTPClient.from_transport(transport)

    older_files = get_older_files(sftp_client)

    # Read previously alerted files to avoid duplicate alerts
    alerted_files = set()
    if os.path.exists(ALERTED_FILE_PATH):
        with open(ALERTED_FILE_PATH, 'r') as f:
            alerted_files = set(f.read().splitlines())

    new_alerts = [f for f in older_files if f not in alerted_files]

    if new_alerts:
        # Send an email for new alerts
        subject = "SFTP Alert: Files older than threshold"
        body = f"The following files are older than {ALERT_AGE_HOURS} hours:\n" + "\n".join(new_alerts)
        send_email(subject, body)

        # Log the newly alerted files
        with open(ALERTED_FILE_PATH, 'a') as f:
            f.write("\n".join(new_alerts) + "\n")

    transport.close()

if __name__ == "__main__":
    check_sftp()
