#!/bin/sh

# Load .env manually for use in this script
export $(grep -v '^#' .env | xargs)

# Default to every hour if not set
CRON_SCHEDULE="${CRON_SCHEDULE:-0 * * * *}"

echo "Using schedule: '$CRON_SCHEDULE'"

# Write dynamic crontab
echo "$CRON_SCHEDULE cd /app && /usr/local/bin/python /app/check_sftp.py >> /var/log/cron.log 2>&1" > /tmp/cronjob
crontab /tmp/cronjob

# Start cron in foreground
cron -f
