# ComputeEngine.md

## ✅ Google Compute Engine (GCE)

Google Compute Engine (GCE) gives you **virtual machines (VMs)** to run applications on Google Cloud.

---

# ✅ 1. What is Compute Engine?

Compute Engine is Google Cloud's **Virtual Machine service** where you can run Linux/Windows servers with full control.

**Real‑time Example:**
You want your Python / Java app to run 24/7 → You launch a GCE VM and deploy your application.

---

# ✅ 2. Key Features

### ✅ Full control VMs (SSH/RDP)

### ✅ Custom machine types (CPU/RAM as you want)

### ✅ Startup scripts

### ✅ Metadata

### ✅ VPC integration

### ✅ Service accounts

### ✅ Autoscaling + Managed Instance Groups

---

# ✅ 3. Types of Compute Engine Machines

1. **E2** – Cheap and good for small apps
2. **N2/N2D** – Balanced performance
3. **C2** – High compute workloads
4. **A2** – GPU machines for ML workloads

**Example:**
A ML team uses **A2 GPU machines** for training models.

---

# ✅ 4. Persistent Disk Types

| Disk Type   | Use Case              |
| ----------- | --------------------- |
| Standard PD | Basic workloads       |
| Balanced PD | App servers           |
| SSD PD      | High-performance apps |

**Example:**
Databases use **SSD Persistent Disks** for high IOPS.

---

# ✅ 5. Ways to Connect to VM

### ✅ SSH via Browser

### ✅ SSH via gcloud

### ✅ SSH keys

### ✅ Cloud IAP (secure tunneling)

**Example:**
Production VMs use **IAP** so they stay private and only authenticated users can access.

---

# ✅ 6. IAM Roles for Compute Engine

| Role                   | Description     |
| ---------------------- | --------------- |
| Compute Admin          | Full control    |
| Compute Viewer         | Read-only       |
| Compute Instance Admin | Manage VMs only |

**Example:**
DevOps team gets **Compute Instance Admin** to start/stop VMs.

---

# ✅ 7. Service Accounts in Compute Engine

A VM uses a **service account** to access GCP services like GCS, Pub/Sub, BigQuery.

## ✅ Common Roles for VM Service Account

* Storage Object Viewer
* Storage Object Admin
* Storage Admin

**Example:**
A VM that downloads data from GCS needs **Storage Object Viewer**.

---

# ✅ 8. ✅ BEST PART — How to Access GCS from Compute Engine (All Possible Ways)

Here are **all possible methods** to access Google Cloud Storage (GCS) from a VM.

---

# ✅ Method 1: Using VM's Service Account (BEST Practice ✅)

### Steps:

1. Create a **service account**
2. Give required roles:

   * Storage Object Viewer (read)
   * Storage Object Admin (write)
3. Attach this service account to VM
4. Use `gsutil` inside VM

### Example Command:

```
gsutil cp gs://my-bucket/file.txt .
```

✅ This is the safest, recommended Google method.

---

# ✅ Method 2: Use Application Default Credentials (ADC)

Just run:

```
gcloud auth application-default login
```

Then use Python, Java, Node.js SDK to access GCS.

**Example (Python):**

```python
from google.cloud import storage
client = storage.Client()
buckets = list(client.list_buckets())
print(buckets)
```

---

# ✅ Method 3: Use a JSON Key File (NOT recommended ❌)

⚠️ Only for local dev testing.

Steps:

1. Create service account
2. Download JSON key
3. Copy key to VM
4. Export credentials:

```
export GOOGLE_APPLICATION_CREDENTIALS="/path/key.json"
```

✅ Works, but risky because key may leak.

---

# ✅ Method 4: Access GCS Using Signed URLs

You can generate pre-signed URLs for **temporary access**.

**Example:**
Backend service creates a signed URL → frontend can upload file to GCS for 15 mins.

---

# ✅ Method 5: Access via GCS Fuse (Mount GCS like a folder)

You can mount GCS bucket as a directory.

Example:

```
gcsfuse my-bucket /mnt/gcs
```

Now VM reads/writes like normal files.

---

# ✅ 9. Firewall Rules for Compute Engine

| Rule        | Purpose  |
| ----------- | -------- |
| allow-ssh   | Port 22  |
| allow-http  | Port 80  |
| allow-https | Port 443 |

**Example:**
To expose a web app on VM, open **port 80/443**.

---

# ✅ 10. Real-Time Architecture Example

A **Python API** running on GCE:

* Connects to Cloud SQL through **private IP**
* Stores logs in **GCS**
* Connects to Redis on Memorystore
* Uses IAM service account for authentication

---

# ✅ 11. Most Common Interview Questions

### ✅ Q1: Difference between Compute Engine and App Engine?

**Answer:**
Compute Engine → VM-based
App Engine → Fully managed serverless

### ✅ Q2: How to secure Compute Engine VM?

* Use IAP
* Disable external IP
* Use firewall rules

### ✅ Q3: How does a VM access GCS?

Most common way → Attach service account with required IAM roles.

---

# ✅ 12. Summary

✅ Compute Engine = Virtual Machines
✅ Apps run 24/7
✅ IAM service account gives access to other GCP services
✅ Multiple ways to access GCS
✅ Best way = VM service account + IAM roles

---

If you want, I can also add:
✅ MIG + Autoscaling examples
✅ VPC internal load balancer setup
✅ Compute Engine Startup Script examples
✅ Cloud SQL private IP connectivity diagrams

## ✅ Types of Compute Engine VMs

Google Cloud Compute Engine provides several VM types depending on your workload and cost needs.

### ### 1. **Standard VM (On‑Demand VM)**

✅ Most common VM type
✅ You pay per second
✅ No commitment
✅ Best for general workloads

**Use Case:** Web servers, APIs, applications.

---

### 2. **Preemptible VM (Old Model – retiring)**

✅ Very cheap (up to 80% less)
❌ Can stop any time (max 24 hours)
❌ Not suitable for critical workloads

**Use Case:** Batch jobs, video rendering.

---

### 3. **Spot VM (New & Recommended)**

✅ Up to **90% cost savings**
✅ Same performance as on‑demand
✅ Can be reclaimed any time when GCP needs capacity
✅ No 24‑hour limit like preemptible VMs

❌ Should not be used for production apps unless designed for restart.

**Use Case:**

* CI/CD runners
* Data processing jobs
* Machine learning training
* Auto-scaled background tasks

**Example creation (Spot VM):**

```bash
gcloud compute instances create spot-vm \
  --machine-type=e2-medium \
  --provisioning-model=SPOT \
  --instance-termination-action=STOP
```

---

### 4. **Committed Use Discount (CUD) VMs**

✅ You commit for **1 or 3 years**
✅ Big discount (up to 57%)
✅ Best for stable, always-on workloads

**Use Case:** Production databases, backend services.

---

### 5. **Shielded VM**

✅ Extra security enabled
✅ Protects against rootkits, firmware attacks, boot-level tampering

**Use Case:** Banking, FinTech, security-critical apps.

---

### 6. **Confidential VM**

✅ Encrypts data **while processing (in-use encryption)**
✅ Uses AMD SEV hardware security

**Use Case:** Healthcare, BFSI, Government workloads.

---

### 7. **Sole-Tenant Nodes**

✅ Dedicated physical server for your company only
✅ No noisy neighbors
✅ Useful for licensing, compliance, BYOL requirements

**Use Case:** SAP workloads, compliance-heavy industries.

---

### 8. **GPU VMs**

✅ Used for ML/AI training, inference, rendering
✅ GPUs like NVIDIA K80, T4, V100, A100

**Use Case:** Deep learning, AI workloads, video processing.

---

### 9. **Machine Families**

Each VM type belongs to a **machine family**:

* **E2** → Cost‑optimized
* **N2 / N2D** → Balanced performance
* **C2 / C3** → Compute‑optimized (high CPU power)
* **M1 / M2** → Memory‑optimized

---

### ✅ Quick Summary Table

| VM Type      | Cost      | Reliability          | Use Case            |
| ------------ | --------- | -------------------- | ------------------- |
| On‑Demand    | High      | ✅✅✅                  | General workloads   |
| Spot         | Very Low  | ✅ (can stop anytime) | Batch, CI/CD, ML    |
| Preemptible  | Very Low  | ✅ (deprecated)       | Batch               |
| CUD          | Low       | ✅✅✅                  | Long‑term workloads |
| Shielded     | High      | ✅✅✅                  | Secure workloads    |
| Confidential | High      | ✅✅✅                  | Govt/Finance        |
| Sole‑Tenant  | Very High | ✅✅✅✅                 | Compliance          |
| GPU          | High      | ✅✅✅                  | AI/ML               |

---

