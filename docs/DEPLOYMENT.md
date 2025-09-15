# Deployment Guide - TechFlow Voice Agent System

## Overview

This guide covers deployment options for the TechFlow Voice Agent System, from development to production environments.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Configuration](#environment-configuration)
3. [Local Development](#local-development)
4. [Docker Deployment](#docker-deployment)
5. [Cloud Deployment](#cloud-deployment)
6. [Production Considerations](#production-considerations)
7. [Monitoring and Logging](#monitoring-and-logging)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

**Minimum Requirements:**
- CPU: 2 cores
- RAM: 4GB
- Storage: 10GB
- Network: Stable internet connection

**Recommended Requirements:**
- CPU: 4+ cores
- RAM: 8GB+
- Storage: 20GB+
- Network: High-speed internet with low latency

### Software Dependencies

- **Python**: 3.10 or higher
- **Node.js**: 16+ (for frontend dependencies)
- **Docker**: 20.10+ (for containerized deployment)
- **Git**: For version control

### External Services

- **Deepgram API**: Voice processing capabilities
- **Google APIs** (optional): Calendar and email integration
- **SSL Certificate**: For HTTPS in production

## Environment Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Required
DEEPGRAM_API_KEY=your_deepgram_api_key_here

# Optional - Google Integration
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:5000/auth/callback

# Application Settings
FLASK_ENV=production
FLASK_DEBUG=false
SECRET_KEY=your_secret_key_here

# Audio Settings
USER_AUDIO_SAMPLE_RATE=48000
AGENT_AUDIO_SAMPLE_RATE=16000

# Business Settings
MOCK_DATA_SIZE_CUSTOMERS=1000
MOCK_DATA_SIZE_APPOINTMENTS=500
MOCK_DATA_SIZE_ORDERS=2000

# Logging
LOG_LEVEL=INFO
LOG_FILE=voice_agent.log

# Security
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
CORS_ENABLED=true

# Performance
MAX_CONNECTIONS=100
WORKER_TIMEOUT=30
```

### Configuration Validation

Validate your configuration:

```bash
python -c "
import os
from dotenv import load_dotenv
load_dotenv()

required_vars = ['DEEPGRAM_API_KEY']
missing = [var for var in required_vars if not os.getenv(var)]

if missing:
    print(f'Missing required environment variables: {missing}')
    exit(1)
else:
    print('Configuration validated successfully')
"
```

## Local Development

### Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/techflow/techflow-voice-agent.git
   cd techflow-voice-agent
   ```

2. **Set up virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run the application:**
   ```bash
   python client.py
   ```

6. **Access the application:**
   Open http://localhost:5000 in your browser

### Development Server Options

**Standard Flask Development:**
```bash
export FLASK_APP=client.py
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=5000
```

**With Auto-reload:**
```bash
python client.py --debug
```

**With Custom Port:**
```bash
python client.py --port=8080
```

## Docker Deployment

### Single Container

1. **Build the image:**
   ```bash
   docker build -t voice-agent-system .
   ```

2. **Run the container:**
   ```bash
   docker run -d \
     --name voice-agent \
     -p 5000:5000 \
     -e DEEPGRAM_API_KEY=your_key_here \
     voice-agent-system
   ```

3. **With environment file:**
   ```bash
   docker run -d \
     --name voice-agent \
     -p 5000:5000 \
     --env-file .env \
     voice-agent-system
   ```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  voice-agent:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DEEPGRAM_API_KEY=${DEEPGRAM_API_KEY}
      - FLASK_ENV=production
    volumes:
      - ./mock_data_outputs:/app/mock_data_outputs
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - voice-agent
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  redis_data:
```

**Deploy with Docker Compose:**
```bash
docker-compose up -d
```

### Multi-stage Docker Build

For optimized production images:

```dockerfile
# Multi-stage Dockerfile
FROM python:3.12-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy Python dependencies
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/ || exit 1

CMD ["gunicorn", "--worker-class", "eventlet", "-w", "1", "--bind", "0.0.0.0:5000", "client:app"]
```

## Cloud Deployment

### AWS Deployment

#### Using AWS ECS

1. **Create ECR repository:**
   ```bash
   aws ecr create-repository --repository-name voice-agent-system
   ```

2. **Build and push image:**
   ```bash
   # Get login token
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com

   # Build and tag
   docker build -t voice-agent-system .
   docker tag voice-agent-system:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/voice-agent-system:latest

   # Push
   docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/voice-agent-system:latest
   ```

3. **Create ECS task definition:**
   ```json
   {
     "family": "voice-agent-task",
     "networkMode": "awsvpc",
     "requiresCompatibilities": ["FARGATE"],
     "cpu": "1024",
     "memory": "2048",
     "executionRoleArn": "arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
     "containerDefinitions": [
       {
         "name": "voice-agent",
         "image": "123456789012.dkr.ecr.us-east-1.amazonaws.com/voice-agent-system:latest",
         "portMappings": [
           {
             "containerPort": 5000,
             "protocol": "tcp"
           }
         ],
         "environment": [
           {
             "name": "FLASK_ENV",
             "value": "production"
           }
         ],
         "secrets": [
           {
             "name": "DEEPGRAM_API_KEY",
             "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:deepgram-api-key"
           }
         ],
         "logConfiguration": {
           "logDriver": "awslogs",
           "options": {
             "awslogs-group": "/ecs/voice-agent",
             "awslogs-region": "us-east-1",
             "awslogs-stream-prefix": "ecs"
           }
         }
       }
     ]
   }
   ```

#### Using AWS Lambda (Serverless)

For serverless deployment, create `serverless.yml`:

```yaml
service: voice-agent-system

provider:
  name: aws
  runtime: python3.12
  region: us-east-1
  environment:
    DEEPGRAM_API_KEY: ${env:DEEPGRAM_API_KEY}

functions:
  app:
    handler: wsgi_handler.handler
    events:
      - http:
          path: /{proxy+}
          method: ANY
      - http:
          path: /
          method: ANY
    timeout: 30

plugins:
  - serverless-python-requirements
  - serverless-wsgi

custom:
  wsgi:
    app: client.app
  pythonRequirements:
    dockerizePip: true
```

### Google Cloud Platform

#### Using Cloud Run

1. **Build and deploy:**
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT_ID/voice-agent-system
   
   gcloud run deploy voice-agent-system \
     --image gcr.io/PROJECT_ID/voice-agent-system \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars DEEPGRAM_API_KEY=your_key_here
   ```

2. **With Cloud Build:**
   Create `cloudbuild.yaml`:
   ```yaml
   steps:
   - name: 'gcr.io/cloud-builders/docker'
     args: ['build', '-t', 'gcr.io/$PROJECT_ID/voice-agent-system', '.']
   - name: 'gcr.io/cloud-builders/docker'
     args: ['push', 'gcr.io/$PROJECT_ID/voice-agent-system']
   - name: 'gcr.io/cloud-builders/gcloud'
     args:
     - 'run'
     - 'deploy'
     - 'voice-agent-system'
     - '--image'
     - 'gcr.io/$PROJECT_ID/voice-agent-system'
     - '--region'
     - 'us-central1'
     - '--platform'
     - 'managed'
     - '--allow-unauthenticated'
   ```

### Microsoft Azure

#### Using Container Instances

```bash
az container create \
  --resource-group myResourceGroup \
  --name voice-agent-system \
  --image voice-agent-system:latest \
  --dns-name-label voice-agent-unique \
  --ports 5000 \
  --environment-variables DEEPGRAM_API_KEY=your_key_here
```

### Heroku Deployment

1. **Create Heroku app:**
   ```bash
   heroku create voice-agent-system
   ```

2. **Set environment variables:**
   ```bash
   heroku config:set DEEPGRAM_API_KEY=your_key_here
   ```

3. **Deploy:**
   ```bash
   git push heroku main
   ```

4. **Create Procfile:**
   ```
   web: gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT client:app
   ```

## Production Considerations

### Security

#### HTTPS Configuration

**Nginx SSL Configuration:**
```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;

    location / {
        proxy_pass http://voice-agent:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /socket.io/ {
        proxy_pass http://voice-agent:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### Security Headers

Add security headers to your web server configuration:

```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
```

### Performance Optimization

#### Application Configuration

**Production Flask Configuration:**
```python
# config.py
import os

class ProductionConfig:
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    # Performance settings
    SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 1 year
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Security settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
```

#### Gunicorn Configuration

Create `gunicorn.conf.py`:
```python
bind = "0.0.0.0:5000"
workers = 1  # Use 1 worker for SocketIO
worker_class = "eventlet"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True
```

#### Load Balancing

For high availability, use multiple instances behind a load balancer:

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  voice-agent-1:
    build: .
    environment:
      - DEEPGRAM_API_KEY=${DEEPGRAM_API_KEY}
    expose:
      - "5000"

  voice-agent-2:
    build: .
    environment:
      - DEEPGRAM_API_KEY=${DEEPGRAM_API_KEY}
    expose:
      - "5000"

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx-lb.conf:/etc/nginx/nginx.conf
    depends_on:
      - voice-agent-1
      - voice-agent-2
```

### Database Configuration

For production, consider replacing mock data with a real database:

```python
# database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://user:pass@localhost/voiceagent')

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

### Caching

Implement caching for better performance:

```python
# cache.py
import redis
import os

redis_client = redis.Redis(
    host=os.environ.get('REDIS_HOST', 'localhost'),
    port=int(os.environ.get('REDIS_PORT', 6379)),
    db=0,
    decode_responses=True
)
```

## Monitoring and Logging

### Application Monitoring

#### Health Check Endpoint

Add a health check endpoint:

```python
@app.route('/health')
def health_check():
    return {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    }
```

#### Metrics Collection

Use Prometheus for metrics:

```python
from prometheus_client import Counter, Histogram, generate_latest

REQUEST_COUNT = Counter('requests_total', 'Total requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('request_duration_seconds', 'Request latency')

@app.route('/metrics')
def metrics():
    return generate_latest()
```

### Logging Configuration

**Production Logging:**
```python
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('logs/voice_agent.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
```

### External Monitoring

#### New Relic Integration

```python
import newrelic.agent

newrelic.agent.initialize('newrelic.ini')

@newrelic.agent.wsgi_application()
def application(environ, start_response):
    return app(environ, start_response)
```

#### Datadog Integration

```python
from datadog import initialize, statsd

initialize(api_key='your_api_key', app_key='your_app_key')

# Track metrics
statsd.increment('voice_agent.requests')
statsd.histogram('voice_agent.response_time', response_time)
```

## Backup and Recovery

### Data Backup

**Automated Backup Script:**
```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"

# Backup mock data
cp -r mock_data_outputs "$BACKUP_DIR/mock_data_$DATE"

# Backup knowledge base
cp -r knowledgebase/mdx "$BACKUP_DIR/knowledge_base_$DATE"

# Backup logs
cp -r logs "$BACKUP_DIR/logs_$DATE"

# Clean old backups (keep last 7 days)
find $BACKUP_DIR -type d -mtime +7 -exec rm -rf {} \;
```

### Disaster Recovery

1. **Database Backup**: Regular database snapshots
2. **Configuration Backup**: Store configuration in version control
3. **Monitoring**: Set up alerts for system failures
4. **Recovery Testing**: Regular disaster recovery drills

## Troubleshooting

### Common Issues

#### Audio Not Working

**Symptoms**: No audio input/output
**Solutions**:
1. Check microphone permissions in browser
2. Verify audio device selection
3. Check PyAudio installation
4. Verify system audio drivers

#### WebSocket Connection Failures

**Symptoms**: Connection drops, no real-time updates
**Solutions**:
1. Check firewall settings
2. Verify proxy configuration
3. Check SSL certificate validity
4. Monitor network connectivity

#### High Memory Usage

**Symptoms**: Application consuming excessive memory
**Solutions**:
1. Monitor audio buffer sizes
2. Check for memory leaks in audio processing
3. Implement proper cleanup in WebSocket handlers
4. Use memory profiling tools

#### API Rate Limiting

**Symptoms**: Deepgram API errors
**Solutions**:
1. Implement request queuing
2. Add retry logic with exponential backoff
3. Monitor API usage
4. Consider API key rotation

### Debug Mode

Enable debug mode for troubleshooting:

```bash
export FLASK_DEBUG=1
export LOG_LEVEL=DEBUG
python client.py
```

### Log Analysis

**Common Log Patterns:**
```bash
# Check for errors
grep -i error logs/voice_agent.log

# Monitor WebSocket connections
grep -i websocket logs/voice_agent.log

# Check API calls
grep -i "deepgram\|api" logs/voice_agent.log

# Monitor performance
grep -i "latency\|duration" logs/voice_agent.log
```

## Scaling Considerations

### Horizontal Scaling

1. **Load Balancer**: Distribute traffic across multiple instances
2. **Session Affinity**: Ensure WebSocket connections stick to same instance
3. **Shared Storage**: Use shared storage for mock data and knowledge base
4. **Database**: Move to shared database for customer data

### Vertical Scaling

1. **CPU**: Increase CPU cores for audio processing
2. **Memory**: Increase RAM for concurrent connections
3. **Storage**: Use SSD for better I/O performance
4. **Network**: Ensure sufficient bandwidth for audio streaming

### Auto-scaling

**AWS Auto Scaling Group:**
```json
{
  "AutoScalingGroupName": "voice-agent-asg",
  "MinSize": 2,
  "MaxSize": 10,
  "DesiredCapacity": 2,
  "TargetGroupARNs": ["arn:aws:elasticloadbalancing:..."],
  "HealthCheckType": "ELB",
  "HealthCheckGracePeriod": 300
}
```

## Maintenance

### Regular Maintenance Tasks

1. **Update Dependencies**: Regular security updates
2. **Log Rotation**: Prevent disk space issues
3. **Certificate Renewal**: SSL certificate updates
4. **Performance Monitoring**: Regular performance reviews
5. **Backup Verification**: Test backup and restore procedures

### Deployment Pipeline

**CI/CD Pipeline Example:**
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Build and push Docker image
      run: |
        docker build -t voice-agent-system .
        docker tag voice-agent-system $ECR_REGISTRY/voice-agent-system:$GITHUB_SHA
        docker push $ECR_REGISTRY/voice-agent-system:$GITHUB_SHA
    
    - name: Deploy to ECS
      run: |
        aws ecs update-service --cluster production --service voice-agent-service --force-new-deployment
```

For additional support, refer to the [API Documentation](API.md) and [Contributing Guide](../CONTRIBUTING.md).