# 🚀 TrustCert AI - Deployment Guide

Hướng dẫn triển khai hoàn chỉnh từ development đến production.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development](#local-development)
3. [Docker Deployment](#docker-deployment)
4. [Cloud Deployment](#cloud-deployment)
5. [Kubernetes](#kubernetes)
6. [Monitoring](#monitoring)
7. [Security Checklist](#security-checklist)
8. [Troubleshooting](#troubleshooting)

---

## 🔧 Prerequisites

### System Requirements
- **CPU:** 4+ cores
- **RAM:** 8GB+ (16GB recommended)
- **Storage:** 50GB+ SSD
- **OS:** Linux (Ubuntu 22.04 LTS recommended)

### Software Requirements
```bash
# Python
python --version  # 3.10+

# Docker
docker --version  # 20.10+
docker-compose --version  # 2.0+

# PostgreSQL
psql --version  # 14+

# Redis
redis-cli --version  # 7+
```

---

## 💻 Local Development

### Step 1: Clone Repository
```bash
git clone https://github.com/vandoanh1999/Trustcert-ai.git
cd Trustcert-ai
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Setup Environment Variables
```bash
cp .env.example .env
nano .env  # Edit with your settings
```

**Critical Environment Variables:**
```env
# Security (MUST CHANGE)
SECRET_KEY=generate-with-openssl-rand-hex-32
JWT_SECRET_KEY=generate-with-openssl-rand-hex-32
ADMIN_API_KEY=generate-secure-key

# Database
DATABASE_URL=postgresql://trustcert:password@localhost:5432/trustcert

# Redis
REDIS_URL=redis://localhost:6379/0

# Blockchain (Optional for development)
ETH_RPC_URL=https://mainnet.infura.io/v3/YOUR_INFURA_KEY
ETH_PRIVATE_KEY=your-private-key-here

# IPFS (Optional)
IPFS_API_KEY=your-pinata-api-key
IPFS_SECRET_KEY=your-pinata-secret-key
```

### Step 5: Generate Cryptographic Keys
```bash
python scripts/generate_keys.py
```

This creates:
- `keys/rsa_private.pem`
- `keys/rsa_public.pem`
- `keys/ecdsa_private.pem`
- `keys/ecdsa_public.pem`

### Step 6: Initialize Database
```bash
# Start PostgreSQL
sudo systemctl start postgresql

# Create database
createdb trustcert

# Run migrations
alembic upgrade head
```

### Step 7: Start Redis
```bash
redis-server --daemonize yes
```

### Step 8: Run Development Server
```bash
uvicorn apps.api.main:app --reload --port 8000
```

Visit: http://localhost:8000/docs

---

## 🐳 Docker Deployment

### Quick Start (All Services)
```bash
# Create .env file
cp .env.example .env

# Edit .env with production settings
nano .env

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f api
```

### Individual Services

#### Start API Only
```bash
docker-compose up -d api
```

#### Start with Monitoring
```bash
docker-compose up -d api postgres redis prometheus grafana
```

#### Scale Workers
```bash
docker-compose up -d --scale worker=4
```

### Health Checks
```bash
# API health
curl http://localhost:8000/api/v1/health

# Database
docker-compose exec postgres pg_isready

# Redis
docker-compose exec redis redis-cli ping
```

---

## ☁️ Cloud Deployment

### Option 1: AWS EC2

#### 1. Launch EC2 Instance
```bash
# Amazon Linux 2 or Ubuntu 22.04
# Instance type: t3.large (minimum)
# Security Group: Allow ports 80, 443, 8000
```

#### 2. Install Docker
```bash
sudo yum update -y
sudo yum install -y docker
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker ec2-user
```

#### 3. Install Docker Compose
```bash
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### 4. Deploy Application
```bash
git clone https://github.com/vandoanh1999/Trustcert-ai.git
cd Trustcert-ai
cp .env.example .env
nano .env  # Configure
docker-compose -f docker-compose.prod.yml up -d
```

#### 5. Setup SSL (Let's Encrypt)
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d trustcert.ai -d www.trustcert.ai
```

### Option 2: DigitalOcean

#### 1. Create Droplet
- **Size:** 4GB RAM / 2 vCPUs
- **OS:** Ubuntu 22.04 LTS
- **Add-ons:** Enable monitoring

#### 2. SSH into Droplet
```bash
ssh root@your-droplet-ip
```

#### 3. Run Installation Script
```bash
curl -sSL https://raw.githubusercontent.com/vandoanh1999/Trustcert-ai/main/scripts/install.sh | bash
```

### Option 3: Railway

#### 1. Install Railway CLI
```bash
npm install -g @railway/cli
railway login
```

#### 2. Initialize Project
```bash
cd Trustcert-ai
railway init
```

#### 3. Set Environment Variables
```bash
railway variables set SECRET_KEY=your-secret
railway variables set DATABASE_URL=your-db-url
```

#### 4. Deploy
```bash
railway up
```

### Option 4: Heroku

#### 1. Create Heroku App
```bash
heroku create trustcert-api
```

#### 2. Add Buildpacks
```bash
heroku buildpacks:add heroku/python
```

#### 3. Provision Add-ons
```bash
heroku addons:create heroku-postgresql:standard-0
heroku addons:create heroku-redis:premium-0
```

#### 4. Deploy
```bash
git push heroku main
```

---

## ⚓ Kubernetes Deployment

### Prerequisites
```bash
# Install kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"

# Install helm
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

### Deploy to Kubernetes

#### 1. Create Namespace
```bash
kubectl create namespace trustcert
```

#### 2. Create Secrets
```bash
kubectl create secret generic trustcert-secrets \
  --from-literal=secret-key=your-secret \
  --from-literal=jwt-secret=your-jwt-secret \
  --from-literal=db-password=your-db-pass \
  -n trustcert
```

#### 3. Deploy Application
```bash
kubectl apply -f kubernetes/ -n trustcert
```

#### 4. Check Status
```bash
kubectl get pods -n trustcert
kubectl get services -n trustcert
```

#### 5. Access Application
```bash
kubectl port-forward service/trustcert-api 8000:8000 -n trustcert
```

### Helm Chart (Recommended)

```bash
# Add Helm repo
helm repo add trustcert https://charts.trustcert.ai
helm repo update

# Install
helm install trustcert trustcert/trustcert-ai \
  --namespace trustcert \
  --create-namespace \
  --set api.replicas=3 \
  --set ingress.enabled=true \
  --set ingress.host=trustcert.yourdomain.com
```

---

## 📊 Monitoring

### Prometheus + Grafana

#### Access Grafana
```bash
# Default credentials
URL: http://localhost:3000
Username: admin
Password: (set in .env GRAFANA_PASSWORD)
```

#### Import Dashboards
1. Go to Dashboards → Import
2. Use dashboard IDs:
   - **FastAPI:** 14781
   - **PostgreSQL:** 9628
   - **Redis:** 11835

### Logs

#### View All Logs
```bash
docker-compose logs -f
```

#### View Specific Service
```bash
docker-compose logs -f api
docker-compose logs -f worker
```

#### Tail Logs
```bash
tail -f logs/app.log
```

### Alerts

#### Setup Email Alerts
Edit `docker/prometheus.yml`:
```yaml
alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']
```

---

## 🔒 Security Checklist

### Before Production

- [ ] Change all default passwords
- [ ] Generate strong SECRET_KEY and JWT_SECRET_KEY
- [ ] Enable HTTPS/TLS
- [ ] Configure firewall (UFW/iptables)
- [ ] Setup rate limiting
- [ ] Enable API key authentication
- [ ] Configure CORS properly
- [ ] Setup backup strategy
- [ ] Enable audit logging
- [ ] Scan for vulnerabilities
- [ ] Setup monitoring alerts
- [ ] Configure DDoS protection
- [ ] Review and limit API permissions

### Security Commands

```bash
# Generate secure keys
openssl rand -hex 32

# Scan for vulnerabilities
docker scan trustcert-api:latest

# Check SSL certificate
openssl s_client -connect trustcert.ai:443

# Test firewall
sudo ufw status
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. API Won't Start
```bash
# Check logs
docker-compose logs api

# Common causes:
# - Database connection failed
# - Redis not accessible
# - Port 8000 already in use

# Solutions:
docker-compose restart postgres redis
lsof -i :8000  # Check what's using port
```

#### 2. Database Connection Error
```bash
# Test connection
docker-compose exec postgres psql -U trustcert -d trustcert

# Reset database
docker-compose down -v
docker-compose up -d postgres
alembic upgrade head
```

#### 3. Worker Not Processing Tasks
```bash
# Check worker logs
docker-compose logs worker

# Restart worker
docker-compose restart worker

# Check Redis connection
docker-compose exec redis redis-cli ping
```

#### 4. High Memory Usage
```bash
# Check resource usage
docker stats

# Restart services
docker-compose restart

# Scale down if needed
docker-compose up -d --scale worker=2
```

### Performance Tuning

#### 1. Database Optimization
```sql
-- Check slow queries
SELECT query, mean_exec_time 
FROM pg_stat_statements 
ORDER BY mean_exec_time DESC 
LIMIT 10;

-- Create indexes
CREATE INDEX idx_model_hash ON certificates(model_hash);
```

#### 2. Redis Optimization
```bash
# Check memory usage
redis-cli info memory

# Set max memory
redis-cli CONFIG SET maxmemory 2gb
redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

#### 3. API Optimization
```python
# Enable caching in .env
CACHE_ENABLED=true
CACHE_TTL_SECONDS=3600

# Increase workers
WORKERS=8  # CPU cores * 2
```

---

## 📞 Support

- 📧 Email: devops@trustcert.ai
- 💬 Discord: [DevOps Channel](https://discord.gg/trustcert)
- 📖 Docs: [docs.trustcert.ai/deployment](https://docs.trustcert.ai/deployment)

---

## ✅ Post-Deployment Checklist

After deployment, verify:

- [ ] API responds at `/api/v1/health`
- [ ] Docs accessible at `/docs`
- [ ] Database migrations applied
- [ ] Redis connected and responding
- [ ] Celery workers running
- [ ] Prometheus scraping metrics
- [ ] Grafana dashboards displaying data
- [ ] SSL certificate valid
- [ ] Backup system configured
- [ ] Monitoring alerts configured
- [ ] Load balancing working (if applicable)
- [ ] Auto-scaling configured (if applicable)

---

**Deployment complete! 🎉**

Your TrustCert AI instance is now running in production!