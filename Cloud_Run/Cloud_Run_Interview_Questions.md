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

## 3. Cloud Run vs Compute Engine
| Cloud Run | Compute Engine |
|----------|----------------|
| No servers to manage | You manage VM/server |
| Auto-scaling built-in | Must configure scaling |
| Pay per request | Pay while running |
| Only containers | Any OS/applications |

---

## 4. Cloud Run vs Cloud Functions
| Cloud Run | Cloud Functions |
|----------|----------------|
| Runs full applications | Runs only a small function |
| Good for Microservices | Good for Event triggers |
| More control | Less control |

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
