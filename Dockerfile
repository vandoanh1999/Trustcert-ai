# TrustCert AI — made by Doanh1102
FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml README.md /app/
COPY apps /app/apps
RUN pip install -U pip && pip install "fastapi==0.115.0" "pydantic==2.9.0" "uvicorn[standard]==0.32.0"
EXPOSE 8000
CMD ["uvicorn","apps.api.main:app","--host","0.0.0.0","--port","8000"]
