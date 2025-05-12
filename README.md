# SFTP Monitor Docker Container

This container monitors an SFTP directory and sends an email alert if any files are older than a configured threshold. The script runs on a schedule defined using cron, and all configuration is managed via environment variables.

I created this out of a need for a portable way to monitor a remote SFTP server for aging files and alert via email when a predefined threshold is reached.

---

## Files Included

- `Dockerfile` – Defines the Python + cron environment  
- `entrypoint.sh` – Sets up cron dynamically using values from `.env`  
- `check_sftp.py` – Python script to check for old files and send email  
- `requirements.txt` – Lists Python dependencies  
- `README.md`

### File Not Included

- `.env` – Create this file yourself based on the template below.

---

## Configuration Instructions

Create a `.env` file and populate it with your own settings:

<details>
<summary><code>.env</code> Template</summary>

```.env
# SFTP configuration
SFTP_HOST=sftp.example.com
SFTP_PORT=22
SFTP_USER=username
SFTP_PASS=password
SFTP_FOLDER=/path/to/folder

# Email configuration
SMTP_SERVER=smtp.example.com
SMTP_PORT=587
SENDER_EMAIL=sender@example.com
SENDER_EMAIL_PASSWORD=your_password
RECEIVER_EMAIL=receiver@example.com

# File alert configuration
ALERT_AGE_HOURS=6

# Cron schedule (default: every 30 minutes)
CRON_SCHEDULE=*/30 * * * *
