#!/bin/sh

# Load environment variables for cron (optional, helpful for debugging)
printenv | grep -v "no_proxy" >> /etc/environment

# Dynamically find the path to Python
PYTHON_PATH=$(which python3)

# Create the cron job with the full path to Python
echo "$CRON_SCHEDULE root $PYTHON_PATH /app/check_sftp.py >> /var/log/cron.log 2>&1" > /etc/cron.d/sftp-check

# Set the correct permissions so cron will run it
chmod 0644 /etc/cron.d/sftp-check

# Install the cron job
crontab /etc/cron.d/sftp-check

# Start cron in the foreground
cron -f
