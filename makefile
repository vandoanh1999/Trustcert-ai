# TrustCert AI - Makefile for Development Automation
# Usage: make [target]

.PHONY: help install setup test run docker clean deploy

# Default target
help:
	@echo "🧠 TrustCert AI - Development Commands"
	@echo "======================================"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install       - Install dependencies"
	@echo "  make setup         - Complete development setup"
	@echo "  make keys          - Generate cryptographic keys"
	@echo ""
	@echo "Development:"
	@echo "  make run           - Run development server"
	@echo "  make test          - Run all tests"
	@echo "  make test-cov      - Run tests with coverage"
	@echo "  make lint          - Run linters"
	@echo "  make format        - Format code"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build  - Build Docker image"
	@echo "  make docker-up     - Start all services"
	@echo "  make docker-down   - Stop all services"
	@echo "  make docker-logs   - View logs"
	@echo ""
	@echo "Database:"
	@echo "  make db-migrate    - Run database migrations"
	@echo "  make db-reset      - Reset database"
	@echo ""
	@echo "Deployment:"
	@echo "  make deploy-prod   - Deploy to production"
	@echo "  make deploy-stage  - Deploy to staging"
	@echo ""
	@echo "Utilities:"
	@echo "  make clean         - Clean temporary files"
	@echo "  make docs          - Generate documentation"

# ============================================================================
# INSTALLATION
# ============================================================================

install:
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt
	pip install -e .

install-dev:
	@echo "📦 Installing dev dependencies..."
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pip install -e .

setup: install-dev
	@echo "🔧 Setting up development environment..."
	cp .env.example .env
	@echo "✅ .env file created - please edit with your settings"
	mkdir -p logs models keys
	@echo "✅ Directories created"
	$(MAKE) keys
	@echo "✅ Setup complete!"

keys:
	@echo "🔑 Generating cryptographic keys..."
	python scripts/generate_keys.py
	@echo "✅ Keys generated in ./keys/"

# ============================================================================
# DEVELOPMENT
# ============================================================================

run:
	@echo "🚀 Starting development server..."
	uvicorn apps.api.main:app --reload --host 0.0.0.0 --port 8000

run-prod:
	@echo "🚀 Starting production server..."
	gunicorn apps.api.main:app \
		--workers 4 \
		--worker-class uvicorn.workers.UvicornWorker \
		--bind 0.0.0.0:8000 \
		--log-level info

worker:
	@echo "👷 Starting Celery worker..."
	celery -A apps.worker.celery_app worker --loglevel=info

beat:
	@echo "⏰ Starting Celery beat..."
	celery -A apps.worker.celery_app beat --loglevel=info

# ============================================================================
# TESTING
# ============================================================================

test:
	@echo "🧪 Running tests..."
	pytest tests/ -v

test-cov:
	@echo "🧪 Running tests with coverage..."
	pytest tests/ -v --cov=apps --cov-report=html --cov-report=term
	@echo "📊 Coverage report: htmlcov/index.html"

test-unit:
	@echo "🧪 Running unit tests..."
	pytest tests/unit/ -v

test-integration:
	@echo "🧪 Running integration tests..."
	pytest tests/integration/ -v

test-watch:
	@echo "👀 Running tests in watch mode..."
	ptw tests/ -- -v

# ============================================================================
# CODE QUALITY
# ============================================================================

lint:
	@echo "🔍 Running linters..."
	flake8 apps/
	pylint apps/
	mypy apps/

format:
	@echo "✨ Formatting code..."
	black apps/ tests/
	isort apps/ tests/
	@echo "✅ Code formatted!"

format-check:
	@echo "🔍 Checking code format..."
	black --check apps/ tests/
	isort --check apps/ tests/

# ============================================================================
# DOCKER
# ============================================================================

docker-build:
	@echo "🐳 Building Docker image..."
	docker-compose build

docker-up:
	@echo "🐳 Starting Docker services..."
	docker-compose up -d
	@echo "✅ Services started!"
	@echo "📚 API Docs: http://localhost:8000/docs"
	@echo "📊 Grafana: http://localhost:3000"

docker-down:
	@echo "🐳 Stopping Docker services..."
	docker-compose down

docker-logs:
	@echo "📋 Viewing logs..."
	docker-compose logs -f

docker-ps:
	@echo "📊 Docker containers status..."
	docker-compose ps

docker-clean:
	@echo "🧹 Cleaning Docker resources..."
	docker-compose down -v
	docker system prune -f

# ============================================================================
# DATABASE
# ============================================================================

db-migrate:
	@echo "🗄️  Running database migrations..."
	alembic upgrade head

db-rollback:
	@echo "⏪ Rolling back last migration..."
	alembic downgrade -1

db-reset:
	@echo "🔄 Resetting database..."
	docker-compose down -v
	docker-compose up -d postgres
	sleep 5
	alembic upgrade head
	@echo "✅ Database reset complete!"

db-shell:
	@echo "🐘 Opening database shell..."
	docker-compose exec postgres psql -U trustcert -d trustcert

# ============================================================================
# DEPLOYMENT
# ============================================================================

deploy-stage:
	@echo "🚀 Deploying to staging..."
	git push staging main
	@echo "✅ Deployed to staging!"

deploy-prod:
	@echo "🚀 Deploying to production..."
	@echo "⚠️  WARNING: Deploying to production!"
	@read -p "Are you sure? (yes/no): " confirm; \
	if [ "$$confirm" = "yes" ]; then \
		git push production main; \
		echo "✅ Deployed to production!"; \
	else \
		echo "❌ Deployment cancelled"; \
	fi

# ============================================================================
# UTILITIES
# ============================================================================

clean:
	@echo "🧹 Cleaning temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .mypy_cache
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info
	@echo "✅ Cleaned!"

docs:
	@echo "📚 Generating documentation..."
	mkdocs build
	@echo "✅ Documentation generated in site/"

docs-serve:
	@echo "📚 Serving documentation..."
	mkdocs serve

# ============================================================================
# MONITORING
# ============================================================================

monitor:
	@echo "📊 Opening monitoring dashboard..."
	open http://localhost:3000  # Grafana

metrics:
	@echo "📈 Opening metrics..."
	open http://localhost:9090  # Prometheus

logs-api:
	@echo "📋 Viewing API logs..."
	docker-compose logs -f api

logs-worker:
	@echo "📋 Viewing worker logs..."
	docker-compose logs -f worker

# ============================================================================
# BACKUP & RESTORE
# ============================================================================

backup:
	@echo "💾 Creating backup..."
	mkdir -p backups
	docker-compose exec -T postgres pg_dump -U trustcert trustcert > backups/backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "✅ Backup created!"

restore:
	@echo "📥 Restoring from backup..."
	@read -p "Enter backup file path: " backup_file; \
	docker-compose exec -T postgres psql -U trustcert trustcert < $$backup_file
	@echo "✅ Backup restored!"

# ============================================================================
# SECURITY
# ============================================================================

security-scan:
	@echo "🔒 Running security scan..."
	bandit -r apps/
	safety check

security-audit:
	@echo "🔐 Running security audit..."
	pip-audit

# ============================================================================
# BENCHMARKING
# ============================================================================

benchmark:
	@echo "⚡ Running benchmarks..."
	pytest tests/performance/ --benchmark-only

load-test:
	@echo "💪 Running load test..."
	locust -f tests/load/locustfile.py --host=http://localhost:8000