import os
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import paramiko
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Ensure log directory exists
os.makedirs("/logs", exist_ok=True)

# Manual logging setup
logger = logging.getLogger("sftp_check")
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("/logs/sftp_check.log")
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def log(message):
    logger.info(message)
    print(message)  # helpful for container stdout

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
ALERTED_FILE_PATH = '/alerted-files/alerted_files.log'

def get_older_files(sftp_client):
    """ Get files older than the configured ALERT_AGE_HOURS. """
    older_files = []
    current_time = time.time()

    try:
        sftp_client.chdir(SFTP_FOLDER)
        log(f"Changed to directory: {sftp_client.getcwd()}")
    except Exception as e:
        log(f"Error changing to SFTP_FOLDER '{SFTP_FOLDER}': {e}")
        return []

    for filename in sftp_client.listdir_attr('.'):
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

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_EMAIL_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
        log("Alert email sent successfully.")
    except Exception as e:
        log(f"Failed to send email: {e}")

def check_sftp():
    """ Check SFTP folder for old files and send alerts. """
    log("===== Starting SFTP check =====")

    # Basic sanity check on critical variables
    missing = []
    for var in ["SFTP_HOST", "SFTP_USER", "SFTP_PASS", "SFTP_FOLDER"]:
        if not os.getenv(var):
            missing.append(var)
    if missing:
        log(f"Missing required environment variables: {', '.join(missing)}")
        log("===== SFTP check aborted =====")
        return

    try:
        transport = paramiko.Transport((SFTP_HOST, SFTP_PORT))
        transport.connect(username=SFTP_USER, password=SFTP_PASS)
        sftp_client = paramiko.SFTPClient.from_transport(transport)

        older_files = get_older_files(sftp_client)

        alerted_files = set()
        if os.path.exists(ALERTED_FILE_PATH):
            with open(ALERTED_FILE_PATH, 'r') as f:
                alerted_files = set(f.read().splitlines())

        new_alerts = [f for f in older_files if f not in alerted_files]

        if new_alerts:
            subject = "SFTP Alert: Check the Bulman Products STFP services. They do not appear to be working!"
            body = f"The following files on the SPS SFTP server are older than {ALERT_AGE_HOURS} hours:\n" + "\n".join(new_alerts)
            send_email(subject, body)

            with open(ALERTED_FILE_PATH, 'a') as f:
                f.write("\n".join(new_alerts) + "\n")

        else:
            log("No new old files to alert.")

        sftp_client.close()
        transport.close()

    except Exception as e:
        log(f"Error during SFTP check: {e}")

    log("===== SFTP check completed =====")

if __name__ == "__main__":
    check_sftp()
