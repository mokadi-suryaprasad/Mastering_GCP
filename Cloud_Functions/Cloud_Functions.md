# Cloud_Functions.md
**Production-grade, real-time Google Cloud Functions (2nd Gen) examples — _No Terraform_**  
Each example includes architecture, Python 3.11 function code, required packages, secure deployment commands, and ops guidance.

> Replace placeholders like `YOUR_PROJECT_ID`, `REGION`, and resource names as needed.

---

## Project 1 — Image Ingestion & Thumbnailer (GCS → CF → Firestore + DLQ)

### 🧩 Use case
When a user uploads an image to a **GCS bucket**, generate a 320px thumbnail, store metadata in **Firestore**, and on failure send the event to a **Pub/Sub dead‑letter topic** for reprocessing.

### 🏗️ Architecture
```
User upload → GCS:images-raw ─(finalize event)→ CF:process_image
                                     │
                                     ├─> GCS:images-thumbs (thumbnail)
                                     ├─> Firestore (metadata)
                                     └─> Pub/Sub:dlq (on error)
```

### 🔐 Security
- Function runs as a **dedicated service account** with the minimum roles:
  - `roles/storage.objectViewer` on raw bucket
  - `roles/storage.objectAdmin` on thumbs bucket (or fine-grained objectCreator)
  - `roles/datastore.user` for Firestore
  - `roles/pubsub.publisher` for DLQ topic
- Buckets use **Uniform Bucket-Level Access**.
- Retries enabled on event trigger; DLQ ensures no data loss.

### 📦 Code (Python 3.11)
`main.py`
```python
import os, json, tempfile
from google.cloud import storage, firestore, pubsub_v1
from PIL import Image

THUMBS_BUCKET = os.getenv("THUMBS_BUCKET")
DLQ_TOPIC = os.getenv("DLQ_TOPIC")

storage_client = storage.Client()
db = firestore.Client()
publisher = pubsub_v1.PublisherClient()

def entrypoint(event, context):
    bucket = event["bucket"]
    name = event["name"]
    try:
        with tempfile.NamedTemporaryFile() as src, tempfile.NamedTemporaryFile(suffix=".jpg") as dst:
            storage_client.bucket(bucket).blob(name).download_to_filename(src.name)
            img = Image.open(src.name)
            img.thumbnail((320, 320))
            out_blob = storage_client.bucket(THUMBS_BUCKET).blob(f"thumb-{name}")
            img.save(dst.name, "JPEG")
            out_blob.upload_from_filename(dst.name, content_type="image/jpeg")

        db.collection("images").document(name).set({
            "original": f"gs://{bucket}/{name}",
            "thumbnail": f"gs://{THUMBS_BUCKET}/thumb-{name}",
            "processed_at": firestore.SERVER_TIMESTAMP,
        })
    except Exception as e:
        topic_path = publisher.topic_path(os.environ["GOOGLE_CLOUD_PROJECT"], DLQ_TOPIC)
        publisher.publish(topic_path, json.dumps({"bucket": bucket, "name": name, "error": str(e)}).encode("utf-8"))
        raise
```

`requirements.txt`
```
google-cloud-storage==2.*
google-cloud-firestore==2.*
google-cloud-pubsub==2.*
Pillow==10.*
```

### 🚀 Deploy (2nd Gen, event trigger)
```bash
# Create resources (one-time)
gcloud storage buckets create gs://images-raw-$USER --location=REGION
gcloud storage buckets create gs://images-thumbs-$USER --location=REGION
gcloud pubsub topics create image-processor-dlq

# Deploy function (2nd gen, event-driven on GCS finalize)
gcloud functions deploy process-image \
  --gen2 \
  --region=REGION \
  --runtime=python311 \
  --entry-point=entrypoint \
  --trigger-event-filters="type=google.cloud.storage.object.v1.finalized" \
  --trigger-event-filters="bucket=images-raw-$USER" \
  --set-env-vars=THUMBS_BUCKET=images-thumbs-$USER,DLQ_TOPIC=image-processor-dlq \
  --min-instances=0 \
  --memory=512Mi \
  --timeout=60s
```

### 🛠 Ops tips
- Add **log-based metric**: filter `severity>=ERROR` for this function → alert policy.
- Use **labels** on objects/documents to track origin/version.
- Configure **retention** on raw bucket; lifecycle to Nearline for thumbs after 30 days.

---

## Project 2 — Secure HTTP Orders API (CF HTTP → Secret Manager → Cloud SQL via SVPC)

### 🧩 Use case
Expose a **low-latency HTTP API** to create orders in **Cloud SQL (PostgreSQL)**. Secrets are read from **Secret Manager**, traffic to DB goes over **Serverless VPC Access**. Protect with **API Gateway (JWT)** or **IAP**.

### 🏗️ Flow
```
Client → API Gateway (JWT/IAP) → CF:orders_api (HTTP)
         │                       └─ Secret Manager → DB URL
         └→ Cloud Logging
```

### 📦 Code (Python 3.11, Flask style handler)
`main.py`
```python
import os
from flask import jsonify, Request
from google.cloud import secretmanager
import sqlalchemy

def _db_url():
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{os.environ['GOOGLE_CLOUD_PROJECT']}/secrets/{os.environ['DB_URL_SECRET']}/versions/latest"
    resp = client.access_secret_version(request={"name": name})
    return resp.payload.data.decode("utf-8")

def entrypoint(request: Request):
    if request.method == "GET":
        return jsonify({"status": "ok"}), 200

    if request.method == "POST":
        engine = sqlalchemy.create_engine(_db_url())
        payload = request.get_json(force=True)
        with engine.begin() as conn:
            conn.execute(sqlalchemy.text(
                "INSERT INTO orders(id, amount) VALUES (:id, :amt)"
            ), {"id": payload["id"], "amt": payload["amount"]})
        return jsonify({"inserted": payload["id"]}), 201

    return ("Method Not Allowed", 405)
```

`requirements.txt`
```
Flask==3.*
google-cloud-secret-manager==2.*
SQLAlchemy==2.*
pg8000==1.*
```

### 🔐 Security & Networking
- Create a **Serverless VPC Connector** and set `--vpc-connector` to reach private DB.
- Restrict invokers: use **API Gateway** or set **ingress internal** and front with a **Load Balancer**.
- Store DB URL in Secret Manager (`orders-db-url`). Grant function SA `Secret Manager Secret Accessor`.

### 🚀 Deploy (HTTP, 2nd Gen)
```bash
# Secret example (edit for your environment)
echo -n "postgresql+pg8000://user:pass@10.20.0.3:5432/orders" | \
  gcloud secrets create orders-db-url --data-file=-

# (Optional) Create a Serverless VPC connector (once)
gcloud compute networks vpc-access connectors create svpc-cf \
  --network=default --region=REGION --range=10.8.0.0/28

# Deploy function
gcloud functions deploy orders-api \
  --gen2 \
  --region=REGION \
  --runtime=python311 \
  --entry-point=entrypoint \
  --trigger-http \
  --set-env-vars=DB_URL_SECRET=orders-db-url \
  --vpc-connector=svpc-cf \
  --egress-settings=private-ranges-only \
  --min-instances=0 \
  --memory=512Mi \
  --timeout=60s \
  --allow-unauthenticated=false
```

### 🛡️ Auth options
- **API Gateway with JWT** (recommended): only the gateway’s service account is granted `run.invoker` on the function.
- **IAP**: put behind HTTPS LB + IAP; function allows only the LB SA.

### 🛠 Ops tips
- Warm critical paths by setting `--min-instances=1`.
- Emit structured logs for order IDs; add **Error Reporting** capture.

---

## Project 3 — Nightly Cost Cleaner (Scheduler → Pub/Sub → CF) + Slack Summary

### 🧩 Use case
Nightly job identifies **idle resources** (e.g., unattached disks) and posts a **Slack** summary; can run in **dry‑run** first, then delete on approval.

### 🏗️ Flow
```
Cloud Scheduler (cron) → Pub/Sub:cost-clean-queue → CF:cost_cleaner
                                               └→ Slack Webhook (summary)
```

### 📦 Code (Python 3.11)
`main.py`
```python
import os, json, base64, requests
from google.cloud import compute_v1

SLACK = os.getenv("SLACK_WEBHOOK")
DEFAULT_DRY = os.getenv("DRY_RUN", "true").lower() == "true"

def entrypoint(event, context):
    # Pub/Sub payload can override dry_run flag
    data = {}
    if "data" in event:
        data = json.loads(base64.b64decode(event["data"]).decode("utf-8"))
    dry = data.get("dry_run", DEFAULT_DRY)

    project = os.environ["GOOGLE_CLOUD_PROJECT"]
    disks_client = compute_v1.DisksClient()

    zones = [z.name for z in compute_v1.ZonesClient().list(project=project)]

    unattached = []
    for zone in zones:
        for disk in disks_client.list(project=project, zone=zone):
            in_use = bool(getattr(disk, "users", None))
            if not in_use:
                unattached.append(f"{zone}/{disk.name}")

    deleted = []
    if not dry:
        for item in unattached[:50]:  # safety cap
            zone, name = item.split("/", 1)
            disks_client.delete(project=project, zone=zone, disk=name)
            deleted.append(item)

    text = f"Cost Cleaner: found {len(unattached)} unattached disks. " \
           f"{'Deleted ' + str(len(deleted)) if not dry else 'Dry-run (no delete)'}."
    try:
        requests.post(SLACK, json={"text": text}, timeout=10)
    except Exception:
        pass

    return {"unattached": len(unattached), "deleted": len(deleted), "dry_run": dry}
```

`requirements.txt`
```
google-cloud-compute==1.*
requests==2.*
```

### 🚀 Setup & Deploy
```bash
# Pub/Sub & Scheduler (once)
gcloud pubsub topics create cost-clean-queue
gcloud scheduler jobs create pubsub nightly-cost-clean \
  --schedule="0 1 * * *" --time-zone="Asia/Kolkata" \
  --topic=cost-clean-queue \
  --message-body='{"dry_run": true}'

# Deploy function
gcloud functions deploy cost-cleaner \
  --gen2 \
  --region=REGION \
  --runtime=python311 \
  --entry-point=entrypoint \
  --trigger-topic=cost-clean-queue \
  --set-env-vars=SLACK_WEBHOOK="https://hooks.slack.com/services/XXX/YYY/ZZZ",DRY_RUN=true \
  --min-instances=0 \
  --memory=1Gi \
  --timeout=540s
```

### 🔐 Least privilege roles
- Function SA: read/compute list, delete disks (scope as narrowly as possible, or operate via label selectors).
- Scheduler SA: Pub/Sub Publisher on `cost-clean-queue`.
- Slack webhook stored in **Secret Manager** and injected via env var at deploy time (recommended).

---

## Cross-cutting Best Practices
- **2nd Gen** functions (Cloud Run under the hood) support **min/max instances**, **CPU**, **concurrency**; tune for latency vs cost.
- Store secrets in **Secret Manager**; never hardcode secrets.
- Emit **structured logs** and create **log-based metrics** for alerts.
- Use **Artifact Registry** for container-based functions if build times get heavy.
- Pin dependency versions and run periodic updates.
- Apply **retry** carefully (idempotent handlers). Use DLQs for event-driven flows.

---

Need Node.js versions, Cloud Build YAML, or a ZIP-able starter folder for each project? I can generate those too.
