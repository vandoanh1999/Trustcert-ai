# ⚡ TrustCert AI - Quick Start Guide

Get TrustCert AI running in **5 minutes**!

---

## 🎯 Option 1: Docker (Recommended)

### Step 1: Clone & Setup
```bash
git clone https://github.com/vandoanh1999/Trustcert-ai.git
cd Trustcert-ai
cp .env.example .env
```

### Step 2: Edit `.env`
```bash
nano .env  # Change SECRET_KEY and JWT_SECRET_KEY
```

Generate secure keys:
```bash
openssl rand -hex 32
```

### Step 3: Start Everything
```bash
docker-compose up -d
```

### Step 4: Verify
```bash
curl http://localhost:8000/api/v1/health
```

### Step 5: Open Docs
Visit: **http://localhost:8000/docs**

---

## 🐍 Option 2: Python (Local)

### Step 1: Prerequisites
```bash
# Python 3.10+
python --version

# PostgreSQL & Redis
brew install postgresql redis  # macOS
# sudo apt install postgresql redis  # Ubuntu
```

### Step 2: Clone & Install
```bash
git clone https://github.com/vandoanh1999/Trustcert-ai.git
cd Trustcert-ai

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Setup Database
```bash
# Start PostgreSQL
brew services start postgresql  # macOS
# sudo systemctl start postgresql  # Linux

# Create database
createdb trustcert
```

### Step 4: Configure Environment
```bash
cp .env.example .env

# Generate keys
python scripts/generate_keys.py

# Edit .env with your settings
nano .env
```

### Step 5: Start Redis
```bash
redis-server --daemonize yes
```

### Step 6: Run Migrations
```bash
alembic upgrade head
```

### Step 7: Start API
```bash
uvicorn apps.api.main:app --reload
```

Visit: **http://localhost:8000/docs**

---

## 🎮 Using Makefile (Easiest)

### All-in-One Setup
```bash
git clone https://github.com/vandoanh1999/Trustcert-ai.git
cd Trustcert-ai
make setup    # Install everything
make run      # Start dev server
```

### Common Commands
```bash
make test          # Run tests
make lint          # Check code quality
make docker-up     # Start with Docker
make docker-logs   # View logs
make docs          # Generate docs
```

---

## ✅ Verify Installation

### 1. Health Check
```bash
curl http://localhost:8000/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "TrustCert AI",
  "version": "2.0.0"
}
```

### 2. Test API
```bash
# Generate model fingerprint
curl -X POST http://localhost:8000/api/v1/verify/fingerprint \
  -H "Content-Type: application/json" \
  -d '{
    "model_path": "/path/to/model.pt",
    "framework": "pytorch"
  }'
```

### 3. Open Interactive Docs
Visit: **http://localhost:8000/docs**

---

## 📊 Access Monitoring

- **API Docs:** http://localhost:8000/docs
- **Grafana:** http://localhost:3000 (admin/admin)
- **Prometheus:** http://localhost:9090
- **IPFS:** http://localhost:5001

---

## 🚀 First API Call

### Python Example
```python
import requests

# Health check
response = requests.get("http://localhost:8000/api/v1/health")
print(response.json())

# Create signed certificate
response = requests.post(
    "http://localhost:8000/api/v1/certify",
    json={
        "model_id": "gpt-4-test",
        "model_hash": "abc123...",
        "algorithm": "RSA"
    },
    headers={"X-API-Key": "your-api-key"}
)
print(response.json())
```

### cURL Example
```bash
curl -X POST http://localhost:8000/api/v1/certify \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "model_id": "gpt-4-test",
    "model_hash": "abc123...",
    "algorithm": "RSA"
  }'
```

---

## 🎓 Next Steps

1. **Read Documentation:** [README.md](README.md)
2. **Explore API:** http://localhost:8000/docs
3. **Run Tests:** `make test`
4. **Deploy:** [DEPLOYMENT.md](DEPLOYMENT.md)
5. **Contribute:** [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 🐛 Troubleshooting

### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Database Connection Error
```bash
# Check PostgreSQL status
brew services list  # macOS
systemctl status postgresql  # Linux

# Restart PostgreSQL
brew services restart postgresql  # macOS
sudo systemctl restart postgresql  # Linux
```

### Redis Connection Error
```bash
# Check Redis
redis-cli ping

# Start Redis
redis-server
```

### Docker Issues
```bash
# Clean everything
docker-compose down -v
docker system prune -f

# Rebuild
docker-compose build --no-cache
docker-compose up -d
```

---

## 💬 Get Help

- 📧 Email: support@trustcert.ai
- 💬 Discord: https://discord.gg/trustcert
- 📖 Docs: https://docs.trustcert.ai
- 🐛 Issues: https://github.com/vandoanh1999/Trustcert-ai/issues

---

## 🎉 You're Ready!

TrustCert AI is now running. Start verifying AI models!

```
   ████████╗██████╗ ██╗   ██╗███████╗████████╗
   ╚══██╔══╝██╔══██╗██║   ██║██╔════╝╚══██╔══╝
      ██║   ██████╔╝██║   ██║███████╗   ██║   
      ██║   ██╔══██╗██║   ██║╚════██║   ██║   
      ██║   ██║  ██║╚██████╔╝███████║   ██║   
      ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚══════╝   ╚═╝   
                                               
          CERT AI - Ready to Verify! ✨
```