# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV METAFLOW_HOME=/metaflow
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy the ingestion flow script, utility, and requirements file
COPY flows/ /app/flows/
COPY requirements.txt /app/requirements.txt

# Copy the bash script to the container
COPY script.sh /app/script.sh

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Make the bash script executable
RUN chmod +x /app/script.sh

# Run the data download and extraction script before starting Metaflow
# RUN python /app/flows/utils/download_data.py

# Define default command to run the bash script
CMD ["/bin/bash", "/app/script.sh"]
