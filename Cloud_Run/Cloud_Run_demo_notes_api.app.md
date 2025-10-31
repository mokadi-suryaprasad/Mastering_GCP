# Cloud Run Small-Scale Demo — "Notes API"

**Project idea (small & interview-friendly):**  
A tiny, containerized REST API called **Notes API** that lets users create, read, update, and delete short text notes. Built with **FastAPI** (Python) and uses **Google Firestore (serverless)** as the backend database — this avoids Cloud SQL/VPC complexity and keeps deployment simple. Deploy the container on **Cloud Run**.

---

## Why this project?
- Small codebase (few files) — great for demos and interviews  
- Uses serverless Firestore — no VPC / Cloud SQL setup  
- Demonstrates containerization, environment configuration, secrets, and CI/CD basics  
- Fast to implement and cheap to run (scales to zero)

---

## Overview
- App: FastAPI exposing `/notes` endpoints  
- Database: Firestore (native mode)  
- Registry: Google Artifact Registry (or Container Registry)  
- Deployment: Cloud Run (fully managed)  
- CI/CD: Optional GitHub Actions

---

## Prerequisites
1. Google Cloud project with billing enabled. Note `PROJECT_ID`.  
2. `gcloud` CLI installed and authenticated: `gcloud auth login` and `gcloud config set project PROJECT_ID`.  
3. `docker` installed and running.  
4. A Firestore database in Native mode (one-time).  
   ```bash
   gcloud services enable firestore.googleapis.com run.googleapis.com artifactregistry.googleapis.com
   gcloud firestore databases create --region=us-central1
   ```
5. Enable Secret Manager (optional): `gcloud services enable secretmanager.googleapis.com`  
6. Create a service account for CI/CD (optional) with `roles/run.admin`, `roles/iam.serviceAccountUser`, `roles/artifactregistry.writer`, `roles/datastore.user`. Download its JSON key for GitHub Actions if using CI.

---

## 1) Project structure
```
notes-api/
├─ app/
│  ├─ main.py
│  └─ requirements.txt
├─ Dockerfile
└─ README.md
```

---

## 2) Application code (FastAPI + Firestore)
Create `app/main.py`:

```py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google.cloud import firestore
import os

# Firestore will use GOOGLE_APPLICATION_CREDENTIALS if running locally with a service account key.
# On Cloud Run, use the default service account with proper IAM permissions.
db = firestore.Client()

app = FastAPI(title="Notes API")

class NoteIn(BaseModel):
    title: str
    content: str

class NoteOut(NoteIn):
    id: str

COLLECTION = "notes"

@app.post("/notes", response_model=NoteOut)
def create_note(note: NoteIn):
    doc_ref = db.collection(COLLECTION).document()
    doc_ref.set(note.dict())
    return {"id": doc_ref.id, **note.dict()}

@app.get("/notes")
def list_notes():
    docs = db.collection(COLLECTION).stream()
    return [{"id": d.id, **d.to_dict()} for d in docs]

@app.get("/notes/{note_id}", response_model=NoteOut)
def get_note(note_id: str):
    d = db.collection(COLLECTION).document(note_id).get()
    if not d.exists:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"id": d.id, **d.to_dict()}

@app.put("/notes/{note_id}", response_model=NoteOut)
def update_note(note_id: str, note: NoteIn):
    doc_ref = db.collection(COLLECTION).document(note_id)
    if not doc_ref.get().exists:
        raise HTTPException(status_code=404, detail="Note not found")
    doc_ref.update(note.dict())
    return {"id": note_id, **note.dict()}

@app.delete("/notes/{note_id}")
def delete_note(note_id: str):
    doc_ref = db.collection(COLLECTION).document(note_id)
    if not doc_ref.get().exists:
        raise HTTPException(status_code=404, detail="Note not found")
    doc_ref.delete()
    return {"deleted": note_id}
```

Create `app/requirements.txt`:
```
fastapi
uvicorn[standard]
google-cloud-firestore
pydantic
```

---

## 3) Dockerfile
Create `Dockerfile` in repo root:

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

## 4) Local testing
1. (Optional) If testing Firestore locally, set `GOOGLE_APPLICATION_CREDENTIALS` environment variable to a service account JSON key that has Firestore permissions:
```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/sa-key.json"
```
2. Build and run locally:
```bash
docker build -t notes-api:local .
docker run -p 8080:8080 -e PORT=8080 notes-api:local
# Visit http://localhost:8080/docs
```

Note: If you don't want to connect to Firestore locally, you can mock the DB or skip DB calls for local tests.

---

## 5) Artifact Registry (push image)
1. Create repo:
```bash
gcloud artifacts repositories create notes-repo   --repository-format=docker --location=us-central1 --description="Notes repo"
```
2. Configure Docker:
```bash
gcloud auth configure-docker us-central1-docker.pkg.dev
```
3. Build & push:
```bash
IMAGE=us-central1-docker.pkg.dev/${PROJECT_ID}/notes-repo/notes-api:v1
docker build -t $IMAGE .
docker push $IMAGE
```

---

## 6) IAM: Service account for Cloud Run
Cloud Run uses the project's default compute service account by default; ensure it has Firestore access:
```bash
SERVICE_ACCOUNT=$(gcloud run services describe notes-api --region=us-central1 --format='value(spec.template.spec.serviceAccountName)') || echo "use default compute service account"
# Grant Datastore/Firestore role
gcloud projects add-iam-policy-binding ${PROJECT_ID}   --member="serviceAccount:${SERVICE_ACCOUNT}" --role="roles/datastore.user"
```
If you deploy before the service exists, instead grant the role to `PROJECT_NUMBER-compute@developer.gserviceaccount.com` (the default) or to a custom SA you will use.

---

## 7) Deploy to Cloud Run
Deploy the image to Cloud Run:

```bash
gcloud run deploy notes-api   --image $IMAGE   --region us-central1   --platform managed   --allow-unauthenticated   --concurrency=80   --max-instances=5
```

Cloud Run will provide a service URL after deployment.

---

## 8) Testing the deployed service
Use the URL from deployment (`gcloud run services describe notes-api --region=us-central1 --format='value(status.url')`):

Create a note:
```bash
curl -X POST $URL/notes -H "Content-Type: application/json" -d '{"title":"Test","content":"Hello world"}'
```

List notes:
```bash
curl $URL/notes
```

---

## 9) Optional: GitHub Actions CI/CD
Create `.github/workflows/deploy.yml`:

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
          IMAGE=us-central1-docker.pkg.dev/${{ secrets.GCP_PROJECT_ID }}/notes-repo/notes-api:${{ github.sha }}
          docker build -t $IMAGE .
          docker push $IMAGE

      - name: Deploy to Cloud Run
        run: |
          gcloud run deploy notes-api             --image $IMAGE             --region us-central1             --platform managed             --allow-unauthenticated
```

Set GitHub secrets: `GCP_PROJECT_ID`, `GCP_SA_KEY` (JSON key content).

---

## 10) Monitoring, Logging & Cost tips
- Use Cloud Logging to view service logs.  
- Configure alerts for error rates or high latency via Cloud Monitoring.  
- Keep `max-instances` low for small-scale to control cost. Cloud Run scales to zero automatically.

---

## 11) Cleanup
```bash
gcloud run services delete notes-api --region=us-central1
gcloud artifacts repositories delete notes-repo --location=us-central1 --quiet
gcloud firestore databases delete --project=${PROJECT_ID} --quiet  # be careful: deletes data
```

---

## Summary
This **Notes API** is a compact, practical project for Cloud Run. It demonstrates containerized deployment, serverless Firestore integration, and optional CI/CD. It's ideal for quick demos, interviews, and learning Cloud Run with minimal infrastructure complexity.

---

If you want, I can:
- Generate the full repo with files and provide a zip.
- Convert the guide into a downloadable Markdown file.
- Provide a Node.js or Go variant instead.
