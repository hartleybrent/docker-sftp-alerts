FROM python:3.11-slim

# Install cron
RUN apt-get update && apt-get install -y cron && ln -s /usr/bin/python3 /usr/bin/python

# Set working directory
WORKDIR /app

# Copy and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy scripts
COPY check_sftp.py entrypoint.sh ./
RUN chmod +x entrypoint.sh check_sftp.py

ENTRYPOINT ["/app/entrypoint.sh"]
