FROM python:3.10-slim

# Install necessary libraries and tools for Raspberry Pi
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    libi2c-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY artifacts/ /app

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]