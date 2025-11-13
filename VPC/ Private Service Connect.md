# Private Service Connect 

This guide shows a **very simple, step‑by‑step demo** of how to use **Private Service Connect (PSC)**. All steps are written in **easy English** so you can understand and run them quickly.

---

## 🌟 What We Are Doing

We will:

1. Create **two VPCs**: Producer and Consumer
2. Deploy a **Cloud Run service** in the Producer VPC
3. Create an **Internal Load Balancer** and **Service Attachment**
4. Create a **PSC Endpoint** from the Consumer VPC
5. Test using a VM inside the Consumer VPC

After this, the Consumer can access the Cloud Run service **using a private IP only**.

---

## 🛠 Variables (Change before running)

```bash
PROJECT_ID="my-project"
REGION="us-central1"

PRODUCER_VPC="producer-vpc"
PRODUCER_SUBNET="producer-subnet"

CONSUMER_VPC="consumer-vpc"
CONSUMER_SUBNET="consumer-subnet"

SERVICE_NAME="hello-service"
SERVICE_ATTACHMENT="hello-attach"
PSC_ENDPOINT="psc-endpoint"
```

---

## 1️⃣ Enable Required APIs

```bash
gcloud services enable compute.googleapis.com run.googleapis.com servicenetworking.googleapis.com \
  --project=$PROJECT_ID
```

---

## 2️⃣ Create VPCs & Subnets

### Producer VPC

```bash
gcloud compute networks create $PRODUCER_VPC --subnet-mode=custom --project=$PROJECT_ID

gcloud compute networks subnets create $PRODUCER_SUBNET \
  --network=$PRODUCER_VPC --region=$REGION --range=10.10.0.0/24 \
  --project=$PROJECT_ID
```

### Consumer VPC

```bash
gcloud compute networks create $CONSUMER_VPC --subnet-mode=custom --project=$PROJECT_ID

gcloud compute networks subnets create $CONSUMER_SUBNET \
  --network=$CONSUMER_VPC --region=$REGION --range=10.20.0.0/24 \
  --project=$PROJECT_ID
```

---

## 3️⃣ Deploy Cloud Run Service

We use a simple **Hello World** service.

```bash
gcloud run deploy $SERVICE_NAME \
  --image=gcr.io/cloudrun/hello \
  --region=$REGION --platform=managed \
  --allow-unauthenticated \
  --project=$PROJECT_ID
```

---

## 4️⃣ Create Internal Load Balancer and Service Attachment

### 4.1 Serverless NEG pointing to Cloud Run

```bash
gcloud compute network-endpoint-groups create ${SERVICE_NAME}-neg \
  --region=$REGION --network-endpoint-type=serverless \
  --cloud-run-service=$SERVICE_NAME \
  --project=$PROJECT_ID
```

### 4.2 Backend Service

```bash
gcloud compute backend-services create ${SERVICE_NAME}-backend \
  --region=$REGION --protocol=HTTP \
  --load-balancing-scheme=internal \
  --project=$PROJECT_ID
```

Add NEG:

```bash
gcloud compute backend-services add-backend ${SERVICE_NAME}-backend \
  --region=$REGION \
  --network-endpoint-group=${SERVICE_NAME}-neg \
  --network-endpoint-group-region=$REGION \
  --project=$PROJECT_ID
```

### 4.3 URL Map

```bash
gcloud compute url-maps create ${SERVICE_NAME}-umap \
  --default-service=${SERVICE_NAME}-backend \
  --project=$PROJECT_ID
```

### 4.4 Target Proxy

```bash
gcloud compute target-http-proxies create ${SERVICE_NAME}-proxy \
  --url-map=${SERVICE_NAME}-umap \
  --project=$PROJECT_ID
```

### 4.5 Internal Forwarding Rule

```bash
gcloud compute forwarding-rules create ${SERVICE_NAME}-ilb \
  --load-balancing-scheme=internal \
  --address=10.10.0.10 \
  --ports=80 \
  --network=$PRODUCER_VPC \
  --subnet=$PRODUCER_SUBNET \
  --region=$REGION \
  --target-http-proxy=${SERVICE_NAME}-proxy \
  --project=$PROJECT_ID
```

### 4.6 Service Attachment

```bash
gcloud compute service-attachments create $SERVICE_ATTACHMENT \
  --region=$REGION \
  --producer-forwarding-rule=${SERVICE_NAME}-ilb \
  --connection-preference=ACCEPT_AUTOMATIC \
  --nat-subnets=$PRODUCER_SUBNET \
  --project=$PROJECT_ID
```

---

## 5️⃣ Create PSC Endpoint (Consumer Side)

```bash
gcloud compute forwarding-rules create $PSC_ENDPOINT \
  --region=$REGION \
  --network=$CONSUMER_VPC \
  --subnet=$CONSUMER_SUBNET \
  --address=10.20.0.50 \
  --ports=80 \
  --target-service-attachment=projects/$PROJECT_ID/regions/$REGION/serviceAttachments/$SERVICE_ATTACHMENT \
  --project=$PROJECT_ID
```

---

## 6️⃣ Test PSC from a Consumer VM

### Create VM

```bash
gcloud compute instances create consumer-test \
  --zone=${REGION}-a --subnet=$CONSUMER_SUBNET \
  --project=$PROJECT_ID
```

### SSH into VM

```bash
gcloud compute ssh consumer-test --zone=${REGION}-a --project=$PROJECT_ID
```

### Test using PSC private IP

```bash
curl http://10.20.0.50
```

Expected output:

```
Hello World
```

---

## 🎉 Summary 

* **Producer VPC** hosts the Cloud Run service.
* We expose it privately using an **Internal Load Balancer**.
* We publish the service using **Service Attachment**.
* **Consumer VPC** creates a PSC endpoint.
* The **Consumer accesses the service using a private IP** only.

---

## ⭐ What is PSC Mainly Used For?

Private Service Connect (PSC) is mainly used to:

* **Securely access a service in one project from another project using only private IPs**.
* No need for public IPs.
* No need for VPC peering, VPN, or interconnect.
* Safe and private communication between projects.

### Example

* **Project A (Producer)** exposes Cloud Run / GKE / API privately.
* **Project B (Consumer)** connects to it using a PSC endpoint (private IP like `10.20.0.50`).

### Real-world use cases

* Share internal APIs across projects.
* Multi-tenant services (one producer → many consumers).
* Connect to Google Managed Services privately (BigQuery, Cloud SQL, Pub/Sub, etc.).

---

* **Producer VPC** hosts the Cloud Run service.
* We expose it privately using an **Internal Load Balancer**.
* We publish the service using **Service Attachment**.
* **Consumer VPC** creates a PSC endpoint.
* The **Consumer accesses the service using a private IP** only.

---

If you want, I can also:
✅ Add a simple diagram
✅ Add Terraform version
✅ Add troubleshooting steps

---

## 🖼 Simple Diagram 

Below is a simple text-based diagram showing **how PSC connects two projects privately**.

```
                ┌──────────────────────────┐
                │     Project A (Producer) │
                │  ------------------------ │
                │  Cloud Run / GKE / VM    │
                │          │                │
                │  Internal Load Balancer  │
                │          │                │
                │  Service Attachment (PSC)│◄──────────────┐
                └──────────┬───────────────┘               │
                           │                               │
                           │  Private Connection (PSC)     │
                           │  No Public IP, No Peering     │
                           ▼                               │
                ┌──────────────────────────┐               │
                │     Project B (Consumer) │               │
                │  ------------------------ │               │
                │  PSC Endpoint (Private IP│ -- 10.20.0.50 │
                │          │                               │
                │     VM / App / Service   │───────────────┘
                │     Accesses privately   │
                └──────────────────────────┘
```

### 💡 Explanation 

* **Project A** exposes its service privately using PSC.
* **Project B** gets a **private IP endpoint** (PSC endpoint).
* When Project B sends a request to this private IP → the request goes **securely to Project A**.
* No internet, no public IP, no VPC peering needed.

---
