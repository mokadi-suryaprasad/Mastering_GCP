# Cloud SQL → GCS Backups with Cloud Functions (Gen2)

Simple, production-style setup to export a **Cloud SQL** database to **Google Cloud Storage** on a **schedule** using **Cloud Functions (2nd Gen)** and **Pub/Sub**. No Terraform.

---

## What you’ll build (in simple words)
- A **cron job** (Cloud Scheduler) sends a message to **Pub/Sub**.
- A **Cloud Function** receives the message and calls the **Cloud SQL Admin API** to **export** your database to a **GCS bucket** as a `.sql` file.
- Backups are stored with a **timestamped filename** (e.g., `gs://my-backups/exports/instance-2025-11-07T01-00-00Z.sql`).

```
Cloud Scheduler (1:00 AM IST) → Pub/Sub → Cloud Function → Cloud SQL Admin API → GCS
```

---

## Prerequisites
- Enable APIs:
  - **Cloud SQL Admin API**
  - **Cloud Functions API**
  - **Cloud Build API** (first-time function deploys)
  - **Cloud Scheduler API**
  - **Pub/Sub API**
- Create or choose:
  - Cloud SQL **instance** (`INSTANCE`) and **database** (`DATABASE`)
  - GCS **bucket** for backups (e.g., `gs://my-sql-backups`)
- Function **service account roles** (least privilege):
  - `roles/cloudsql.admin` (to call export)
  - `roles/storage.objectAdmin` (or narrower: objectCreator on the backup bucket path)
  - `roles/pubsub.subscriber` is handled by the trigger automatically

> Tip: Use **uniform bucket-level access** and limit access to the backups path (e.g., `gs://my-sql-backups/exports/`).

---

## Function code (Python 3.11)

**`main.py`**
```python
import os
import json
import base64
from datetime import datetime, timezone
from google.oauth2 import service_account  # Only needed if using explicit creds; on CF use default
from googleapiclient.discovery import build

# ENV VARS (set at deploy time)
PROJECT_ID   = os.getenv("PROJECT_ID")
INSTANCE     = os.getenv("INSTANCE")       # e.g., "my-sql-instance"
DATABASE     = os.getenv("DATABASE")       # e.g., "appdb" (for MySQL); for Postgres you can leave this empty to export all DB objects in the default DB
BACKUP_BUCKET = os.getenv("BACKUP_BUCKET") # e.g., "my-sql-backups"
FOLDER_PREFIX = os.getenv("FOLDER_PREFIX", "exports")  # e.g., "exports" or "daily"
DB_ENGINE     = os.getenv("DB_ENGINE", "mysql")        # "mysql" or "postgres"

def _export_uri() -> str:
    # Timestamped filename; use UTC to simplify
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    filename = f"{INSTANCE}-{ts}.sql"
    return f"gs://{BACKUP_BUCKET}/{FOLDER_PREFIX}/{filename}"

def _export_body():
    uri = _export_uri()
    body = {
        "exportContext": {
            "fileType": "SQL",
            "uri": uri,
        }
    }
    # For MySQL, you can specify databases to export
    if DB_ENGINE.lower().startswith("mysql") and DATABASE:
        body["exportContext"]["databases"] = [DATABASE]
    # For Postgres, omitting databases typically exports from the default database context.
    # If you need specific schemas/tables, adjust via db-specific options (outside this minimal example).
    return body

def entrypoint(event, context):
    # Optional message overrides via Pub/Sub: {"database":"appdb","folder_prefix":"daily"}
    try:
        if "data" in event:
            payload = json.loads(base64.b64decode(event["data"]).decode("utf-8"))
        else:
            payload = {}
    except Exception:
        payload = {}

    global DATABASE, FOLDER_PREFIX
    DATABASE = payload.get("database", DATABASE)
    FOLDER_PREFIX = payload.get("folder_prefix", FOLDER_PREFIX)

    service = build("sqladmin", "v1beta4", cache_discovery=False)
    request = service.instances().export(project=PROJECT_ID, instance=INSTANCE, body=_export_body())
    response = request.execute()

    # The export is an async operation; we return the operation name so you can check status via logs or follow-up.
    op = response.get("name", "operation")
    return {"status": "EXPORT_TRIGGERED", "operation": op, "target_uri": _export_uri()}
```

**`requirements.txt`**
```
google-api-python-client==2.*
google-auth==2.*
```

> The function uses **Application Default Credentials** on Gen2, so you normally **do not** need to ship a key. Just ensure the **function’s service account** has the roles above.

---

## Deploy & Schedule (replace values)

> Use **your** project and **region**. The example timezone is **Asia/Kolkata** (IST).

```bash
# 1) Create a bucket for backups (once)
gcloud storage buckets create gs://my-sql-backups --location=REGION

# 2) Create Pub/Sub topic (once)
gcloud pubsub topics create cloudsql-backup-queue

# 3) Deploy the function (Gen2, Pub/Sub trigger)
gcloud functions deploy cloudsql-backup \
  --gen2 \
  --region=REGION \
  --runtime=python311 \
  --entry-point=entrypoint \
  --trigger-topic=cloudsql-backup-queue \
  --set-env-vars=PROJECT_ID=YOUR_PROJECT_ID,INSTANCE=my-sql-instance,DATABASE=appdb,DB_ENGINE=mysql,BACKUP_BUCKET=my-sql-backups,FOLDER_PREFIX=exports \
  --memory=512Mi \
  --timeout=540s

# 4) Create the Scheduler job (01:00 IST every day)
gcloud scheduler jobs create pubsub nightly-cloudsql-backup \
  --schedule="0 1 * * *" \
  --time-zone="Asia/Kolkata" \
  --topic=cloudsql-backup-queue \
  --message-body='{"folder_prefix":"daily"}'
```

> To trigger ad-hoc backups with a different DB or folder prefix:
```bash
gcloud pubsub topics publish cloudsql-backup-queue \
  --message='{"database":"appdb","folder_prefix":"on-demand"}'
```

---

## Verify exports
- Open **Cloud Storage** → your bucket → `exports/` (or your `FOLDER_PREFIX`) → look for files like `my-sql-instance-YYYY-MM-DDTHH-MM-SSZ.sql`.
- In **Logs Explorer**, filter by the function name and check the returned **operation name** to audit/trace the export calls.
- You can also check the **Cloud SQL Admin API** operations list for export status.

---

## Notes (MySQL vs Postgres)
- **MySQL**: You can specify `databases` in the export body to export a single DB. CSV exports are also available if needed.
- **PostgreSQL**: The Admin API supports SQL export; omitting `databases` typically exports from the default DB context. For schema/table-specific exports or `pg_dump` options, consider a containerized job (Cloud Run/Batch) running `pg_dump` with a **private connection** via Serverless VPC. This guide focuses on the **built-in export** for simplicity and portability.

---

## Security best practices
- Use a **dedicated service account** per function.
- Grant only **minimum** roles (`cloudsql.admin` for export; **objectCreator** on the backup prefix is safer than project-wide objectAdmin).
- Keep backups in a bucket with **retention** and **lifecycle rules** (e.g., delete after 30/60/90 days).
- Consider **KMS**-encrypted buckets (CMEK) for compliance.
- Don’t publish service account keys; rely on **Workload Identity** / default credentials.

---

## Troubleshooting
- **Permission denied**: Ensure the function’s SA has `roles/cloudsql.admin` and write access to your bucket.
- **Bucket not found**: Confirm the bucket name and region. Cross-region exports are supported but keep data locality in mind.
- **Timeouts**: Increase `--timeout` if your database is large; exports are asynchronous but the API call must return successfully.
- **Huge DBs**: Consider **sharding** by table (CSV exports), or run `pg_dump`/`mysqldump` in Cloud Run/Batch for more control.
