# Cloud Run + VPC → Secure Access 

This hands‑on guide shows two things:

1) **Outbound secure access**: Cloud Run securely reaches **private resources inside a VPC** (e.g., a VM or Cloud SQL with Private IP) using a **Serverless VPC Access connector**.

2) **Inbound secure access**: Your users reach Cloud Run **securely** via a **Load Balancer** (with **IAP** or **internal‑only**) while Cloud Run **doesn’t allow direct public ingress**.

You can do one or both parts depending on your need.

---

## What you’ll build (high level)

**Part A — Outbound:**
```
Cloud Run (no public egress) --(VPC Connector)--> VPC Subnet --> Private service (VM/SQL)
```

**Part B — Inbound (two options):**
- **Option 1 (External + IAP):**
```
Users (internet) --HTTPS--> External LB (IAP + Cloud Armor) --Serverless NEG--> Cloud Run
Cloud Run ingress: "internal-and-cloud-load-balancing" (no direct public access)
```
- **Option 2 (Internal only):**
```
Clients in VPC --HTTPS--> Internal LB (regional) --Serverless NEG--> Cloud Run
Cloud Run ingress: "internal-and-cloud-load-balancing" (no internet access)
```

---

## Prerequisites
- A GCP Project with **billing enabled**
- Roles (or Owner): `compute.admin`, `iam.serviceAccountAdmin`, `run.admin`, `iap.admin`, `compute.securityAdmin`
- **gcloud** installed and authenticated: `gcloud init`
- A region that supports Cloud Run, VPC connectors, and Load Balancers (e.g., `asia-south1` or `us-central1`)

> Tip: Replace `PROJECT_ID`, `REGION`, and IP ranges with your values.

---

## Set variables (copy‑paste)
```bash
PROJECT_ID="your-project-id"
REGION="asia-south1"        # or your preferred region
VPC_NAME="demo-vpc"
SUBNET_NAME="demo-subnet"
SUBNET_RANGE="10.10.0.0/24"
CONNECTOR_NAME="run-connector"
CONNECTOR_RANGE="10.8.0.0/28"   # small /28 just for the connector
SVC_ACCT="run-invoker@${PROJECT_ID}.iam.gserviceaccount.com"
RUN_SERVICE="run-to-vpc"
RUN_IMAGE="gcr.io/cloudrun/hello"  # replace later if you build your own
LB_NAME="run-external-lb"
BACKEND_NAME="run-neg"
URLMAP_NAME="run-url-map"
PROXY_NAME="run-https-proxy"
FWDRULE_NAME="run-https-rule"
CERT_NAME="run-managed-cert"
HOSTNAME="your-domain.example.com" # for external LB + IAP option
``` 

---

# Part A — Outbound: Cloud Run → VPC (Serverless VPC Access)

### 1) Create VPC + Subnet
```bash
gcloud compute networks create ${VPC_NAME}   --subnet-mode=custom   --project=${PROJECT_ID}

gcloud compute networks subnets create ${SUBNET_NAME}   --network=${VPC_NAME}   --region=${REGION}   --range=${SUBNET_RANGE}   --project=${PROJECT_ID}
```

### 2) (Demo target) Create a private VM with an internal web server
This gives us something **inside the VPC** to call from Cloud Run.

```bash
# Allow internal TCP/80 from connector range
gcloud compute firewall-rules create allow-connector-to-vm   --network=${VPC_NAME}   --allow=tcp:80   --source-ranges=${CONNECTOR_RANGE}

# Create a tiny VM that serves HTTP on internal IP only
VM_NAME="demo-private-vm"
STARTUP_SCRIPT='#! /bin/bash
apt-get update -y && apt-get install -y nginx
sed -i "s/Welcome to nginx!/Hello from PRIVATE VM!/" /var/www/html/index.nginx-debian.html
systemctl enable nginx && systemctl restart nginx
'

gcloud compute instances create ${VM_NAME}   --zone=${REGION}-a   --subnet=${SUBNET_NAME}   --no-address   --metadata=startup-script="${STARTUP_SCRIPT}"

# Capture the VM's internal IP
VM_IP=$(gcloud compute instances describe ${VM_NAME} --zone=${REGION}-a   --format='get(networkInterfaces[0].networkIP)')
echo "VM internal IP: ${VM_IP}"
```

> The VM has **no public IP**. It listens on port 80 and returns *Hello from PRIVATE VM!*.

### 3) Create a Serverless VPC Access connector
```bash
gcloud compute networks vpc-access connectors create ${CONNECTOR_NAME}   --region=${REGION}   --network=${VPC_NAME}   --range=${CONNECTOR_RANGE}

# Wait until connector state is READY before continuing
```

### 4) Deploy Cloud Run service that calls the private VM
For a quick demo, we’ll use a minimal container that proxies a request to the VM. You can use any web app — just ensure it sends an HTTP request to `http://${VM_IP}`.

**Option A (use sample container with an env var):**
```bash
# Deploy a simple hello image and make it call the VM via curl on request using a tiny script
# (Easiest is to build your own small Flask/Node service that fetches ${VM_IP}.)
# Here we show the connectivity flags; plug your own image.

gcloud run deploy ${RUN_SERVICE}   --image=${RUN_IMAGE}   --region=${REGION}   --vpc-connector=${CONNECTOR_NAME}   --vpc-egress=all   --ingress=internal-and-cloud-load-balancing   --no-allow-unauthenticated   --set-env-vars=TARGET_URL=http://${VM_IP}
```

> **Key flags:**
> - `--vpc-connector` + `--vpc-egress=all` routes egress via your VPC.
> - `--ingress=internal-and-cloud-load-balancing` prevents direct public access; only an LB (or internal) can reach it.
> - `--no-allow-unauthenticated` forces auth by default (good practice).

### 5) Verify outbound connectivity (from Cloud Run to VM)
- Temporarily **invoke** your service through a Load Balancer (see Part B), or do a quick **authenticated curl** using the service URL if you left ingress open during testing.
- The response should include **Hello from PRIVATE VM!** fetched via the VPC connector.

> If you get timeouts: check firewall rule source range = connector range, and `--vpc-egress` is set.

---

# Part B — Inbound: Secure access **to** Cloud Run
Pick **one** of the two.

## Option 1 — External HTTPS Load Balancer + IAP (recommended)
Gives you a public HTTPS endpoint with **Google Sign‑In / OAuth** protection via **Identity‑Aware Proxy** and optional **Cloud Armor** WAF.

### 1) Ensure Cloud Run doesn’t accept direct public ingress
We already set `--ingress=internal-and-cloud-load-balancing` and `--no-allow-unauthenticated` above.

### 2) Create a Serverless NEG pointing to your Cloud Run service
```bash
gcloud compute network-endpoint-g-groups create ${BACKEND_NAME}   --region=${REGION}   --network-endpoint-type=serverless   --cloud-run-service=${RUN_SERVICE}   --cloud-run-region=${REGION}
```
*(If the above command errors on the group type, it’s likely a typo. The correct command is `network-endpoint-groups`.)*

### 3) Create a backend service and attach the NEG
```bash
BS_NAME="run-backend-service"
gcloud compute backend-services create ${BS_NAME}   --global   --load-balancing-scheme=EXTERNAL_MANAGED   --protocol=HTTP

gcloud compute backend-services add-backend ${BS_NAME}   --global   --network-endpoint-group=${BACKEND_NAME}   --network-endpoint-group-region=${REGION}
```

### 4) SSL cert for your domain (managed)
```bash
gcloud compute ssl-certificates create ${CERT_NAME}   --domains=${HOSTNAME}
```
> Point your domain’s DNS **A record** to the LB IP (created in step 6). The cert will provision automatically.

### 5) URL map and HTTPS proxy
```bash
gcloud compute url-maps create ${URLMAP_NAME}   --default-service=${BS_NAME}

gcloud compute target-https-proxies create ${PROXY_NAME}   --url-map=${URLMAP_NAME}   --ssl-certificates=${CERT_NAME}
```

### 6) Create a global external forwarding rule (get public IP)
```bash
gcloud compute forwarding-rules create ${FWDRULE_NAME}   --global   --load-balancing-scheme=EXTERNAL_MANAGED   --target-https-proxy=${PROXY_NAME}   --ports=443
```

> Note the IP assigned; update your DNS `A` record to this IP for `${HOSTNAME}`.

### 7) Turn on Identity‑Aware Proxy (IAP)
1. In **Cloud Console → Security → Identity‑Aware Proxy**, locate your **HTTPS Load Balancer** resource.
2. **Enable IAP** for the backend service.
3. Add the **user/group** emails that should have access.

> Result: Only authenticated users you allow can reach Cloud Run through the LB. Direct calls to the Cloud Run URL will fail due to the ingress restriction.

### 8) (Optional) Add Cloud Armor
- Create a security policy (rate limiting, bot management, IP allow/deny)
- Attach it to the **backend service** `run-backend-service`.

---

## Option 2 — Internal HTTPS Load Balancer (VPC‑only)
Expose Cloud Run **inside** the VPC only. Works when clients live on the same VPC / via VPN / Interconnect / VPC peering.

### 1) Use an **internal** managed LB with a serverless NEG
```bash
INT_BS="run-int-backend"
INT_URLMAP="run-int-url-map"
INT_PROXY="run-int-https-proxy"
INT_FWDRULE="run-int-https-rule"

# Backend (regional, internal)
gcloud compute backend-services create ${INT_BS}   --region=${REGION}   --load-balancing-scheme=INTERNAL_MANAGED   --protocol=HTTP

gcloud compute backend-services add-backend ${INT_BS}   --region=${REGION}   --network-endpoint-group=${BACKEND_NAME}   --network-endpoint-group-region=${REGION}

# URL map & proxy
gcloud compute url-maps create ${INT_URLMAP}   --region=${REGION}   --default-service=${INT_BS}

gcloud compute target-https-proxies create ${INT_PROXY}   --region=${REGION}   --url-map=${INT_URLMAP}   --ssl-certificates=${CERT_NAME}  # you can also use self‑managed certs for internal clients

# Forwarding rule on an internal IP in your subnet
gcloud compute forwarding-rules create ${INT_FWDRULE}   --region=${REGION}   --load-balancing-scheme=INTERNAL_MANAGED   --network=${VPC_NAME}   --subnet=${SUBNET_NAME}   --target-https-proxy=${INT_PROXY}   --ports=443
```

> Clients in the VPC can now call the internal IP (or internal DNS) to reach Cloud Run. No internet exposure.

---

## Testing

### Test outbound path
- Hit your Cloud Run endpoint (through LB). Your app should **fetch `${VM_IP}`** and return the VM’s response.
- If you used IAP, sign in with an allowed account; unauthenticated users should be blocked.

### Test ingress lock‑down
- Try opening the **direct Cloud Run URL**: it should be blocked (ingress restricted).
- Try the **LB URL / domain**: it should work (and prompt for sign‑in if IAP is on).

---

## Troubleshooting
- **Connector not READY**: wait a few minutes; check `gcloud compute networks vpc-access connectors describe`.
- **Timeouts to private VM**: 
  - Firewall must allow **source = connector range** to port 80.
  - `--vpc-egress=all` (or `private-ranges-only` if your VM is in RFC1918 space).
  - VM must have service listening on the **internal IP**.
- **403 on direct Cloud Run URL**: expected with `--ingress=internal-and-cloud-load-balancing`.
- **IAP 403**: Add your user/group to IAP access list.
- **TLS cert (external)**: ensure DNS A record points to LB IP; wait for provisioning.

---

## Security best practices (quick list)
- Keep Cloud Run **private**: `--ingress=internal-and-cloud-load-balancing`, no unauthenticated.
- Put **IAP** in front of external LB; add **Cloud Armor** policy.
- Use **Workload Identity** for Cloud Run to access GCP APIs.
- Principle of least privilege on the Cloud Run **service account**.
- Prefer **Private IP** for Cloud SQL/Redis and reach them via the **VPC connector**.
- Restrict egress with `--vpc-egress=private-ranges-only` where possible.

---

## Cleanup (avoid charges)
```bash
# Delete forwarding rules / proxies / url maps / backend services
gcloud compute forwarding-rules delete ${FWDRULE_NAME} --global -q || true
gcloud compute target-https-proxies delete ${PROXY_NAME} -q || true
gcloud compute url-maps delete ${URLMAP_NAME} -q || true
gcloud compute backend-services delete run-backend-service --global -q || true

# Internal LB pieces
gcloud compute forwarding-rules delete ${INT_FWDRULE} --region=${REGION} -q || true
gcloud compute target-https-proxies delete ${INT_PROXY} --region=${REGION} -q || true
gcloud compute url-maps delete ${INT_URLMAP} --region=${REGION} -q || true
gcloud compute backend-services delete ${INT_BS} --region=${REGION} -q || true

# Serverless NEG
gcloud compute network-endpoint-groups delete ${BACKEND_NAME} --region=${REGION} -q || true

# Cloud Run service
gcloud run services delete ${RUN_SERVICE} --region=${REGION} -q || true

# VPC connector
gcloud compute networks vpc-access connectors delete ${CONNECTOR_NAME} --region=${REGION} -q || true

# VM + firewall
gcloud compute instances delete ${VM_NAME} --zone=${REGION}-a -q || true
gcloud compute firewall-rules delete allow-connector-to-vm -q || true

# VPC + subnet
gcloud compute networks subnets delete ${SUBNET_NAME} --region=${REGION} -q || true
gcloud compute networks delete ${VPC_NAME} -q || true

# SSL cert (if created)
gcloud compute ssl-certificates delete ${CERT_NAME} -q || true
```

---

## FAQ
**Q: Does Cloud Run live *inside* my VPC?**  
A: No. Cloud Run is fully managed and not directly in your VPC. You use a **Serverless VPC Access connector** for **egress to VPC**. For **ingress**, use **LB + serverless NEG** and restrict Cloud Run ingress.

**Q: Do I need Public IPs anywhere?**  
A: For **Option 1 (External LB)**, yes (on the LB). For **Option 2 (Internal LB)**, no — traffic stays inside the VPC.

**Q: Can I use Private Service Connect (PSC)?**  
A: Yes; PSC can publish an internal endpoint for Cloud Run in some patterns, but Internal HTTPS LB + serverless NEG is the most straightforward for apps.

**Q: What about Cloud SQL?**  
A: Use **Private IP** and the **VPC connector**. The Cloud SQL Auth Proxy (or libraries) handles auth; networking goes through the connector.

---

**You’re done!** You have both **outbound** (Cloud Run → VPC) and **inbound** (Users → LB → Cloud Run) secured patterns. Adapt the snippets to your environment and app image.
