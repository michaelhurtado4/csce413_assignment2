# Use Python slim image
FROM python:3.11-slim

WORKDIR /app

# Copy honeypot script
COPY honeypot.py .

# Install paramiko and required tools
RUN apt-get update && apt-get install -y python3-pip \
    && pip3 install --no-cache-dir paramiko \
    && mkdir -p /logs \
    && chmod 777 /logs \
    && apt-get clean

# Expose SSH port
EXPOSE 22

# Run honeypot
CMD ["python3", "honeypot.py"]
