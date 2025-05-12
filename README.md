# SFTP Monitor Docker Container

This container monitors an SFTP directory and sends an email alert if any files are older than a configured threshold. The script is run on a schedule defined using cron, and all configuration is managed via environment variables. I created this out of a need for a portable way to monitor a remote STPF server for aging files and alert via email one a pre-defined threshold was reached. 

---

Files Included:
- `Dockerfile` – Defines the Python + cron environment
- `entrypoint.sh` – Sets up cron dynamically using values from `.env`
- `check_sftp.py` – Python script to check for old files and send email
- `requirements.txt` – Load ython dependencies
- `.env` – Environment variables for config
- `README.md`

==================

Configuration Instructions:

Edit the `.env` file with your own settings:

# SFTP configuration
SFTP_HOST=sftp.example.com
SFTP_PORT=22 (or alternate)
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

# Cron schedule (default: every 30 minutes. Follows cron standards.
CRON_SCHEDULE=*/30 * * * *

===============


# Build and Run

docker build -t sftp-monitor .

# Run the container detached

docker run -d --env-file .env sftp-monitor

