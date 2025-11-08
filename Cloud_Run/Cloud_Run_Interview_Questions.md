# Cloud Run Interview Questions 

## 1. What is Cloud Run?
Cloud Run is a *serverless* service in Google Cloud.
It runs applications from **Docker containers** without needing to manage servers.

You only provide your **container** → Cloud Run runs it, scales it, and stops when not needed.

---

## 2. Why do we use Cloud Run?
We use Cloud Run when we:
- Don’t want to manage servers/VMs
- Want automatic scaling
- Want to pay only when the app is used
- Have apps running in Docker containers

**Example:** Small API gets traffic only during day. Cloud Run scales to **zero** at night → saves money.

---

### Cloud Run vs Compute Engine

| Feature | **Cloud Run** | **Compute Engine** |
|--------|---------------|--------------------|
| Server Management | No servers to manage | You manage the VM/server |
| Scaling | Auto-scales automatically | You must configure scaling |
| Billing Model | **Pay per request** | **Pay while running** |
| Workload Type | Only containerized applications | Any OS / any application |

---

### What does **Pay per Request** mean?

- In **Cloud Run**, you pay **only when your application is actually processing requests**.
- If there are **no requests**, Cloud Run **scales to zero** and **you pay ₹0** during idle time.

**Example:**  
If your service receives no traffic for 3 hours → **No billing for those 3 hours**.

---

### What does **Pay while Running** mean?

- In **Compute Engine**, you pay for the **VM as long as it is running**, even if **no user is accessing** your application.
- The billing continues until you **stop or delete** the VM.

**Example:**  
Even if your server is idle for 3 hours → **You are still billed for those 3 hours**.

---

### Easy Technical Summary

- **Cloud Run** → Billed based on **actual usage** (when requests are being processed).
- **Compute Engine** → Billed based on **allocated resources** (CPU/Memory) while the VM is running.


---

## 4. Cloud Run vs Cloud Functions 

### Overview

| Feature | **Cloud Run** | **Cloud Functions** |
|--------|----------------|--------------------|
| What it Runs | **Full containerized applications** | **Single small function / code snippet** |
| Use Case | Best for **microservices**, APIs, web applications | Best for **event-driven tasks** (e.g., file upload, Pub/Sub message) |
| Control Level | **More control** over environment, runtime, dependencies | **Less control**, platform manages most of the runtime |
| Language Support | Any language or runtime as long as it runs in a container | Supported runtimes only (Node.js, Python, Go, Java, etc.) |
| Scaling Behavior | Auto-scales based on HTTP requests, can scale to **zero** when idle | Auto-scales based on **events**, also scales to **zero** when no triggers occur |
| Networking | Can easily run inside **VPC** | Requires VPC connector setup for private network access |
| **Cost Model** | **Pay per request + CPU/Memory time during request** | **Pay per function invocation + execution duration + memory used** |
| Deployment Unit | Container image | Function code |

---

### Cost Model Explanation

#### Cloud Run (Pay per Request)
- You pay **only when your app is actively handling a request**.
- If there is **no traffic**, Cloud Run **scales to zero** and costs **₹0**.
- Billing is based on:
  - Number of requests
  - CPU & Memory usage **while the request is being processed**
  - Request duration (milliseconds)

#### Cloud Functions (Pay per Execution)
- You pay **each time your function is triggered**.
- If no events occur → **₹0 cost**.
- Billing is based on:
  - Number of invocations
  - Execution time
  - Memory allocated to the function

---

### How Cloud Functions are Triggered

Cloud Functions are **event-driven**, meaning the code runs **only when an event happens**.

| Trigger Type | Source | Example | What Causes the Function to Run |
|--------------|--------|---------|--------------------------------|
| **HTTP Trigger** | HTTP/HTTPS Request | API call | Function runs when the endpoint is hit |
| **Cloud Storage** | Bucket Events | File upload/delete | Function runs to process the file |
| **Pub/Sub** | Messaging System | Message published | Function runs to handle the message |
| **Cloud Scheduler** | Cron-like Job | Every 5 minutes | Function runs on schedule |
| **Firebase Trigger** | Firestore / Realtime DB | Document created/updated | Function reacts to DB change |

**Important:**  
If **no event** occurs → the function stays idle → **no cost**.

---

### Easy Summary (Interview Ready)

- **Cloud Run** is used to **run full applications or microservices**.  
  It gives more control and supports any language via containers.  
  **Billing is based on request usage.**

- **Cloud Functions** is used for **small tasks that run automatically when triggered by an event**.  
  No server management; only code runs when needed.  
  **Billing is based on number of function executions.**

---



---

## 5. What applications can run on Cloud Run?
Any app that:
1. Runs in a **Docker container**
2. Can handle **HTTP requests**

Examples:
- Backend APIs
- Web applications
- Microservices

---

## 6. What are Revisions in Cloud Run?
Each deployment creates a **new revision**.
Helps with:
- Rollback
- Traffic splitting (Blue/Green deployment)

---

## 7. What is Traffic Splitting?
We can split traffic between versions.

Example:
- 90% → Old version
- 10% → New version for testing

---

## 8. What is Autoscaling in Cloud Run?
Cloud Run increases or decreases the number of running containers automatically based on traffic.

Example:
- 1 user → 1 instance
- 10,000 users → many instances auto-created

---

## 9. Public vs Private Access
- **Public**: Anyone on the internet can access
- **Private**: Only allowed users or internal services can access

---

## 10. How to Deploy to Cloud Run?

Step 1: Build Docker image  
Step 2: Push to Artifact Registry  
Step 3: Deploy:
```
gcloud run deploy service-name --image <image-url> --region <region>
```

---

## 11. Real Example
A Python Flask API containerized and deployed to Cloud Run.

Benefits:
- No server setup
- Automatic scaling
- Cost-effective

---

## 12. Logs in Cloud Run
Go to:
Cloud Run → Select Service → Logs  
Logs stored in **Cloud Logging**.

---

## 13. Pricing
You pay only when the app is running (per request).
When no traffic → **0 cost**.

---

## Summary
Cloud Run is best when:
- You use Docker
- Need auto-scaling
- Want low maintenance
- Want to reduce cost

Great for **APIs** and **Microservices**.
