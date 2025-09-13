FROM python:3.12-slim

# Install system dependencies including portaudio
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install -r requirements.txt gunicorn eventlet

# Copy project files
COPY . .

# Expose port 5000
EXPOSE 5000

# Run with gunicorn
CMD ["gunicorn", "--worker-class", "eventlet", "-w", "1", "--bind", "0.0.0.0:5000", "client:app"] 