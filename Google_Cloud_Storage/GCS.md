# ✅ Google Cloud Storage (GCS) 

---

## ✅ 1. What is Google Cloud Storage?

GCS is like a **big online folder** where you store files such as:

* photos
* videos
* logs
* backups
* application files

It is **fully managed**, **very fast**, and **very safe**.

📌 Think of it like **Google Drive for your cloud applications**.

---

## ✅ 2. What is a Bucket?

A **bucket** is a folder inside GCS where you store your files.

Example:

* bucket: `my-app-logs`
* file inside bucket: `app.log`

---

## ✅ 3. Create a Bucket — Step-by-Step (Console)

1. Open **Google Cloud Console**
2. Go to **Storage → Buckets**
3. Click **Create Bucket**
4. Enter a unique name → `my-demo-bucket-1234`
5. Choose Location → **Region** (ex: asia-south1)
6. Choose Storage Class → **Standard**
7. Access Control → **Uniform** (recommended)
8. Click **Create** ✅

Done! Your bucket is ready.

---

## ✅ 4. Create a Bucket — CLI (gcloud)

```bash
gcloud storage buckets create gs://my-demo-bucket-1234 \
  --location=asia-south1
```

---

## ✅ 5. Upload Files to Bucket

### Console:

1. Open your bucket
2. Click **Upload File**
3. Choose any file → upload ✅

### CLI:

```bash
gcloud storage cp file.txt gs://my-demo-bucket-1234
```

---

## ✅ 6. Download Files

CLI:

```bash
gcloud storage cp gs://my-demo-bucket-1234/file.txt .
```

---

## ✅ 7. Make a File Public (Public URL)

> ⚠️ Public files can be viewed by anyone.

### Console:

1. Open the file → Click **Permissions**
2. Add:

   * Principal: **allUsers**
   * Role: **Storage Object Viewer**

### CLI:

```bash
gcloud storage objects update gs://my-demo-bucket-1234/file.txt \
  --add-acl-grant=entity=allUsers,role=READER
```

Public URL format:

```
https://storage.googleapis.com/BUCKET_NAME/FILE_NAME
```

---

## ✅ 8. GCS Storage Classes (Easy Explanation)

### 1. **Standard** → For daily use

### 2. **Nearline** → Access once a month

### 3. **Coldline** → Access once a quarter

### 4. **Archive** → Access once a year (cheapest)

Example:

* Logs → Standard
* Backup → Coldline/Archive

---

## ✅ 9. How GCS Permissions Work (Easy Way)

GCS uses **IAM roles**.

### Common roles:

| Role                     | What it can do         |
| ------------------------ | ---------------------- |
| **Storage Viewer**       | Read files             |
| **Storage Object Admin** | Upload/Delete files    |
| **Storage Admin**        | Full control on bucket |

### Add permission:

Console → IAM → Add → Enter email → Select role

---

## ✅ 10. Access GCS from Compute Engine (Easy Ways)

There are **three** simple ways:

### ✅ Way 1 — Give VM a Service Account (BEST)

1. Create a **service account**
2. Give role → **Storage Object Admin**
3. Attach service account to VM → **Edit → Service Account**
4. Restart VM

Now the VM can access GCS without keys.

### ✅ Way 2 — Use gcloud inside VM

```bash
gcloud storage cp file.txt gs://my-demo-bucket
```

### ✅ Way 3 — Use a JSON Key (Not recommended)

Useful only for external servers.

---

## ✅ 11. Real-Time Example: App Uploading Logs to GCS

A Python app on a VM writes logs to GCS:

```python
from google.cloud import storage

client = storage.Client()
bucket = client.get_bucket("my-demo-bucket-1234")
blob = bucket.blob("logs/app.log")
blob.upload_from_filename("app.log")
```

---

## ✅ 12. GCS Best Practices (Super Simple)

✅ Use **Uniform access**
✅ Enable **Bucket Versioning**
✅ Use **Lifecycle rules** (auto delete old files)
✅ Never make whole buckets public
✅ Use **Service Accounts**, not JSON Keys

---

## ✅ 13. Troubleshooting (Easy)

**❌ Upload denied?**
→ You don’t have Storage Object Admin role.

**❌ Cannot download?**
→ File is private.

**❌ Public URL not opening?**
→ You forgot to give `allUsers` → Reader.

---

If you want, I can add:
✅ Architecture diagram
✅ Real-time scenario questions
✅ GCS signed URLs example
✅ Node.js / Java / Go code samples
✅ Terraform version of GCS

# GCS.md — Google Cloud Storage (Step-by-step, Easy & Practical)

This file is a clear, step-by-step guide to **Google Cloud Storage (GCS)** — concepts, console & CLI steps, code examples, security, best practices, and real-world usage. Replace placeholders like `PROJECT_ID`, `BUCKET_NAME`, `REGION` with your values.

---

## ✅ What is Google Cloud Storage (GCS)?

GCS is an object storage service for storing files (objects) in **buckets**. Use it for backups, static website hosting, data lakes, logs, and more.

* **Object** = file (image.mp4, data.csv)
* **Bucket** = container for objects
* **Key** = object name/path

---

## ✅ Storage Classes (choose based on access pattern)

* **Standard** — frequently accessed data (low latency)
* **Nearline** — accessed < once a month (cheaper)
* **Coldline** — accessed < once a quarter (cheaper)
* **Archive** — long-term, rarely accessed (cheapest)

**Tip:** Choose lower-cost class for colder data and move automatically with lifecycle rules.

---

## ✅ Locations (Regional vs Multi-Regional)

* **Regional** — stores data in one region (e.g., `asia-south1`) — cheaper, lower latency for regional workloads.
* **Multi-Regional / Dual-Regional** — distributed across multiple regions — higher availability.

---

## ✅ Step-by-step: Create a Bucket (Console)

1. Console → Navigation menu → **Storage → Browser**
2. Click **Create bucket**
3. Choose a globally unique **Bucket name** (e.g., `my-app-bucket-123`)
4. Select **Location type** (Regional / Multi-Regional / Dual-Regional)
5. Choose **Storage class** (Standard / Nearline / Coldline / Archive)
6. Set **Access control** (Uniform bucket-level access recommended)
7. Configure **Encryption** (Google-managed or Customer-managed)
8. Click **Create**

---

## ✅ Step-by-step: Create a Bucket (gsutil CLI)

```bash
# Create standard bucket in asia-south1
gsutil mb -l asia-south1 gs://my-app-bucket-123/

# Create with storage class
gsutil mb -c nearline -l us-central1 gs://my-nearline-bucket/
```

---

## ✅ Upload & Download Objects

### Console: Upload

* Open bucket → Click **Upload files** or **Upload folder**

### CLI: gsutil

```bash
# Upload
gsutil cp localfile.txt gs://my-app-bucket-123/

# Download
gsutil cp gs://my-app-bucket-123/localfile.txt ./

# List objects
gsutil ls gs://my-app-bucket-123/
```

---

## ✅ Make an Object Public (Static Website example)

**Console:** Select object → Click **Edit permissions** → Add **AllUsers** with **Reader** role.

**CLI:**

```bash
gsutil acl ch -u AllUsers:R gs://my-app-bucket-123/index.html
```

**Tip:** Use Uniform bucket-level access + Signed URLs instead of public ACLs for security.

---

## ✅ Signed URLs (Temporary access without IAM)

Generate a signed URL to give time-limited access to an object.

```bash
# With gcloud (newer tool) - using service account key
gcloud storage sign-url --duration=15m gs://my-app-bucket-123/secret.pdf
```

Use the URL in `curl` or browser.

---

## ✅ Versioning & Object Lifecycle

### Enable Versioning (Console)

Bucket → Settings → **Object versioning** → Enable

### Lifecycle Example (Move to Coldline after 30 days)

```json
{
  "rule": [
    {
      "action": { "type": "SetStorageClass", "storageClass": "COLDLINE" },
      "condition": { "age": 30 }
    }
  ]
}
```

Apply with `gsutil lifecycle set lifecycle.json gs://BUCKET`.

---

## ✅ Encryption Options

* **Google-managed keys (default)** — easiest.
* **Customer-managed keys (CMEK)** — use Cloud KMS keys you control.

**Console:** Bucket → Edit → Encryption → Select CMEK

---

## ✅ Access Control: IAM vs ACLs

* **Uniform bucket-level access (recommended)**: Use IAM only (simpler & secure).
* **ACLs (legacy)**: Per-object permissions (more complex). Prefer IAM.

**Common IAM roles:**

* `roles/storage.objectViewer` → read objects
* `roles/storage.objectCreator` → create objects
* `roles/storage.objectAdmin` → read/write/delete
* `roles/storage.admin` → full admin on bucket

---

## ✅ How Compute Engine VMs access GCS (Recap)

1. **Attach a Service Account to the VM** (best): grant `roles/storage.objectViewer` or `roles/storage.objectAdmin`. No keys needed.
2. **Use Application Default Credentials** via `gcloud auth application-default login` (dev only).
3. **Use JSON key file** (not recommended).
4. **Signed URLs** for temporary access.
5. **gcsfuse** to mount bucket as filesystem (good for simple workloads).

---

## ✅ Programmatic Access (Examples)

### Python (Cloud Storage client)

```python
from google.cloud import storage
client = storage.Client()
bucket = client.get_bucket('my-app-bucket-123')
blob = bucket.blob('file.txt')
blob.upload_from_filename('localfile.txt')
```

### Node.js

```js
const {Storage} = require('@google-cloud/storage');
const storage = new Storage();
await storage.bucket('my-app-bucket-123').upload('localfile.txt');
```

---

## ✅ Advanced Features

* **Requester Pays** — charge requester for egress costs
* **Retention Policies** — prevent deletion for a minimum period
* **Bucket Lock / WORM** — immutable storage for compliance
* **VPC Service Controls (Service Perimeter)** — protect data exfiltration
* **Transfer Service** — move large datasets from other clouds or S3

---

## ✅ Monitoring & Logging

* Use **Cloud Audit Logs** to track object changes and bucket access.
* Use **Cloud Monitoring** metrics for request counts, latency, and egress.

---

## ✅ Cost Tips

* Use correct storage class for data age.
* Delete old versions if not needed.
* Use lifecycle rules to move data to cheaper storage classes.
* Use regional buckets for compute-heavy workloads to reduce egress.

---

## ✅ Quick Troubleshooting

* `AccessDenied` → check IAM role, object ACL, uniform access settings.
* `NotFound` → check bucket name and object path.
* High egress costs → check cross-region access patterns.

---

## ✅ Real-World Examples

1. **Static Website Hosting**: Host HTML/CSS/JS in a bucket and enable public access or use Cloud CDN.
2. **Application Backups**: Daily DB dump to Nearline / Coldline via scheduled job.
3. **Big Data Lake**: Store raw logs in Standard, move to Nearline/Coldline with lifecycle rules.

---

## ✅ Commands Cheat Sheet

```bash
# Create bucket
gsutil mb -l asia-south1 gs://my-bucket/

# Upload
gsutil cp file.txt gs://my-bucket/

# List
gsutil ls gs://my-bucket/

# Download
gsutil cp gs://my-bucket/file.txt ./

# Set bucket lifecycle
gsutil lifecycle set lifecycle.json gs://my-bucket/

# Enable versioning
gsutil versioning set on gs://my-bucket/
```

---

## ✅ Final Notes

GCS is simple but powerful. Start with correct **bucket location, storage class, and access model**. Automate lifecycle and use service accounts for secure access.

If you want, I can:

* Add **diagrams (Mermaid)** showing architecture
* Add **code examples** for Java, Go, and bash
* Create a **one-page cheat sheet PDF**
* Add **VPC-SC** playground examples
