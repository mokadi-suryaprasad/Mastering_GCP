# Cloud Run Demo Project — "Bookstore API"

**Project idea:**  
A simple, containerized RESTful API called **Bookstore API** that allows Create / Read / Update / Delete (CRUD) operations for books. We'll build it with **Python (FastAPI)**, containerize with Docker, store metadata in **Cloud SQL (Postgres)**, and deploy to **Google Cloud Run** with a CI/CD pipeline using **GitHub Actions**. The guide includes secure secrets, VPC access for Cloud SQL, logging, and cleanup steps.

---

## Overview
- App: FastAPI (Python) exposing CRUD endpoints for `/books`
- Database: Cloud SQL (Postgres)
- Container registry: Google Artifact Registry (or Container Registry)
- Deployment: Cloud Run (fully managed)
- CI/CD: GitHub Actions (build → push → deploy)
- Extras: Secret Manager for DB credentials, VPC Connector for private DB access, Cloud Monitoring + Logs

---

## Prerequisites
1. Google Cloud project (with billing enabled). Note the PROJECT_ID.
2. `gcloud` CLI installed and authenticated (`gcloud auth login`).
3. `docker` installed and running.
4. GitHub repository for your project.
5. Enable APIs:
   ```bash
   gcloud services enable run.googleapis.com        sqladmin.googleapis.com        artifactregistry.googleapis.com        secretmanager.googleapis.com        cloudbuild.googleapis.com        compute.googleapis.com
   ```
6. Install Cloud SDK components if needed:
   ```bash
   gcloud components install beta
   ```

---

## 1) Application code (FastAPI)
Create these files in your repo.

**app/main.py**
```py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import psycopg2
from psycopg2.extras import RealDictCursor

app = FastAPI()

DB_HOST = os.environ.get("DB_HOST")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
DB_NAME = os.environ.get("DB_NAME")
DB_PORT = os.environ.get("DB_PORT", "5432")

def get_conn():
    return psycopg2.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASS, dbname=DB_NAME, port=DB_PORT
    )

class Book(BaseModel):
    id: int | None = None
    title: str
    author: str
    pages: int

@app.on_event("startup")
def startup():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS books (
      id SERIAL PRIMARY KEY,
      title TEXT NOT NULL,
      author TEXT NOT NULL,
      pages INT NOT NULL
    )""")
    conn.commit()
    cur.close()
    conn.close()

@app.post("/books", response_model=Book)
def create_book(b: Book):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        "INSERT INTO books (title, author, pages) VALUES (%s, %s, %s) RETURNING id, title, author, pages",
        (b.title, b.author, b.pages),
    )
    book = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return book

@app.get("/books")
def list_books():
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id, title, author, pages FROM books ORDER BY id")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

@app.get("/books/{book_id}", response_model=Book)
def get_book(book_id: int):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT id, title, author, pages FROM books WHERE id = %s", (book_id,))
    book = cur.fetchone()
    cur.close()
    conn.close()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book
```

**app/requirements.txt**
```
fastapi
uvicorn[standard]
psycopg2-binary
```

**Dockerfile**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app /app
ENV PORT 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

---

## 2) Local test
Build and run locally:
```bash
docker build -t bookstore-api:local .
docker run -p 8080:8080   -e DB_HOST=host.docker.internal -e DB_USER=pguser -e DB_PASS=pgpass -e DB_NAME=books   bookstore-api:local
# Visit http://localhost:8080/docs
```

---

## 3) Create Cloud SQL (Postgres) instance
1. Create Postgres instance (private IP recommended if using VPC connector):
```bash
gcloud sql instances create bookstore-sql   --database-version=POSTGRES_15   --tier=db-f1-micro   --region=us-central1
```
2. Create database and user:
```bash
gcloud sql databases create books --instance=bookstore-sql
gcloud sql users create pguser --instance=bookstore-sql --password="SOME_STRONG_PASSWORD"
```
3. Note the private IP (if using private ip) or public ip.

---

## 4) Artifact Registry (store container images)
1. Create a repository (Docker format):
```bash
gcloud artifacts repositories create bookstore-repo   --repository-format=docker   --location=us-central1   --description="Container repo for bookstore"
```
2. Configure Docker to authenticate:
```bash
gcloud auth configure-docker us-central1-docker.pkg.dev
```
3. Build and push image:
```bash
IMAGE=us-central1-docker.pkg.dev/${PROJECT_ID}/bookstore-repo/bookstore:v1
docker build -t $IMAGE .
docker push $IMAGE
```

---

## 5) Secret Manager
Store DB password:
```bash
echo -n "SOME_STRONG_PASSWORD" | gcloud secrets create bookstore-db-pass --data-file=- --replication-policy="automatic"
```

Grant Cloud Run service account access later (secret accessor role).

---

## 6) VPC Connector (if Cloud SQL private IP)
If Cloud SQL uses private IP, create Serverless VPC connector:
```bash
gcloud compute networks vpc-access connectors create cr-connector   --region=us-central1 --network=default --range=10.8.0.0/28
```

---

## 7) Deploy to Cloud Run
Deploy using image, connect to VPC connector, and set env vars from Secret Manager.

```bash
gcloud run deploy bookstore-api   --image $IMAGE   --region us-central1   --platform managed   --add-cloudsql-instances ""   --vpc-connector cr-connector   --set-env-vars DB_HOST=<PRIVATE_IP_OR_HOST>,DB_USER=pguser,DB_NAME=books,DB_PORT=5432   --update-secrets DB_PASS=projects/${PROJECT_ID}/secrets/bookstore-db-pass:latest   --concurrency=80   --max-instances=10   --allow-unauthenticated
```

Notes:
- If using Cloud SQL Proxy method, add `--add-cloudsql-instances` with the instance connection name and use the Cloud SQL Python connector or Unix socket path. The example above uses direct DB host; choose what fits your topology.
- `--update-secrets` maps Secret Manager secret into env var (requires gcloud SDK v359+). Alternative: use Secret Manager client in code.

---

## 8) IAM: Allow Secret & Cloud SQL access
Grant the Cloud Run runtime service account access to use the secret and to connect to Cloud SQL:
```bash
SERVICE_ACCOUNT=$(gcloud run services describe bookstore-api --region=us-central1 --format='value(spec.template.spec.serviceAccountName)')
gcloud secrets add-iam-policy-binding bookstore-db-pass   --member="serviceAccount:${SERVICE_ACCOUNT}" --role="roles/secretmanager.secretAccessor"

gcloud projects add-iam-policy-binding ${PROJECT_ID}   --member="serviceAccount:${SERVICE_ACCOUNT}" --role="roles/cloudsql.client"
```

---

## 9) CI/CD: GitHub Actions (simple)
Create `.github/workflows/cloud-run-deploy.yml`:

```yaml
name: Build and Deploy to Cloud Run
on:
  push:
    branches: [ main ]

jobs:
  build-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Cloud SDK
        uses: google-github-actions/setup-gcloud@v1
        with:
          project_id: ${{ secrets.GCP_PROJECT_ID }}
          service_account_key: ${{ secrets.GCP_SA_KEY }}
          export_default_credentials: true

      - name: Configure Docker auth
        run: gcloud auth configure-docker us-central1-docker.pkg.dev

      - name: Build and push image
        run: |
          IMAGE=us-central1-docker.pkg.dev/${{ secrets.GCP_PROJECT_ID }}/bookstore-repo/bookstore:${{ github.sha }}
          docker build -t $IMAGE .
          docker push $IMAGE

      - name: Deploy to Cloud Run
        run: |
          gcloud run deploy bookstore-api             --image $IMAGE             --region us-central1             --platform managed             --vpc-connector cr-connector             --set-env-vars DB_HOST=${{ secrets.DB_HOST }},DB_USER=pguser,DB_NAME=books,DB_PORT=5432             --update-secrets DB_PASS=projects/${{ secrets.GCP_PROJECT_ID }}/secrets/bookstore-db-pass:latest             --allow-unauthenticated
```

Secrets to set in GitHub:
- `GCP_PROJECT_ID`, `GCP_SA_KEY` (base64 JSON key), `DB_HOST` (private IP or host), and ensure Secret Manager secret exists.

---

## 10) Testing & Healthcheck
- Visit the Cloud Run URL and `/docs` for interactive API docs (FastAPI).
- Use `curl` to verify endpoints:
```bash
curl -X POST "$URL/books" -H "Content-Type: application/json"   -d '{"title":"Sapiens","author":"Yuval Noah Harari","pages":464}'
curl $URL/books
```
- Configure Cloud Run readiness/liveness health checks by implementing a `/health` endpoint and using Cloud Run settings to ensure traffic routing only to healthy instances.

---

## 11) Monitoring & Logs
- Logs: View in Cloud Logging (select Cloud Run service).
- Metrics: Use Cloud Monitoring to create uptime checks and alerting policies (CPU, request latency, error rate).
- Add structured logs in your app to improve observability.

---

## 12) Custom Domain & HTTPS
Map a custom domain to Cloud Run service via:
```bash
gcloud run domain-mappings create --service bookstore-api --domain example.com --region us-central1
```
Follow DNS instructions from GCP; Cloud Run provisions HTTPS certificates automatically.

---

## 13) Cost optimizations
- Use autoscale to zero for idle periods.
- Set sensible `max-instances`.
- Adjust CPU & memory to fit load.
- Use Cloud SQL smallest tier for dev/testing.

---

## 14) Cleanup (avoid unexpected charges)
```bash
gcloud run services delete bookstore-api --region=us-central1
gcloud artifacts repositories delete bookstore-repo --location=us-central1 --quiet
gcloud sql instances delete bookstore-sql --quiet
gcloud compute networks vpc-access connectors delete cr-connector --region=us-central1 --quiet
gcloud secrets delete bookstore-db-pass --quiet
```

---

## 15) Extensions / Next steps (optional)
- Add authentication with Identity Platform / OAuth.
- Use Cloud SQL Proxy or the Cloud SQL Python connector for IAM DB auth.
- Add Redis (Memorystore) for caching.
- Use Cloud Build triggers instead of GitHub Actions.
- Add Blue/Green or Canary deployments using traffic splitting.

---

## Quick command cheatsheet
```bash
# Deploy (example)
gcloud run deploy bookstore-api --image us-central1-docker.pkg.dev/$PROJECT_ID/bookstore-repo/bookstore:v1 --region us-central1 --platform managed

# View URL
gcloud run services describe bookstore-api --region=us-central1 --format='value(status.url)'

# Tail logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=bookstore-api" --limit 50 --format json

# Delete
gcloud run services delete bookstore-api --region=us-central1
```

---

## Summary
This project demonstrates a realistic end-to-end Cloud Run deployment: containerized app, secure secrets, database connectivity, CI/CD, monitoring, and cleanup. It's great for interviews and real-world demos.

---

**If you want**, I can:
- Generate the full repo structure + files (ready-to-run) and provide a zip.
- Produce a GitHub Actions workflow with Cloud Build alternative.
- Add Cloud SQL Proxy code example and IAM-based DB auth.
