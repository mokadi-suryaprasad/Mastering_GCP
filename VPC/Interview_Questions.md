# GCP Interview Questions

---

## ✅ 1. What is a VPC?

A VPC is your **private network** inside Google Cloud.
Just like your own WiFi network but in the cloud.

---

## ✅ 2. What is a Subnet?

A subnet is a **small part** of a VPC.
You divide the big network into smaller networks.

---

## ✅ 3. Difference between VPC and Subnet

* **VPC** = Big network
* **Subnet** = Small section inside the big network

---

## ✅ 4. What is a Firewall Rule?

Rules that decide:

* What traffic is **allowed**
* What traffic is **blocked**

Example: Allow port 80 → website works.

---

## ✅ 5. How Firewall Priority Works

* Smaller number = higher priority
* Rule with priority **100** is checked before **200**

---

## ✅ 6. What is a Route?

A route tells where traffic should go.
Like Google Maps for your VPC.

---

## ✅ 7. What is Cloud NAT?

Cloud NAT gives **internet access** to private VMs or GKE nodes **without public IP**.

---

## ✅ 8. What is Cloud Router?

Cloud Router helps your VPC talk to your on‑prem network using **BGP**.

---

## ✅ 9. What is VPC Peering?

It connects two VPCs **privately**.

Limitations:

* Cannot have overlapping IPs
* No transitive peering (A↔B, B↔C does NOT mean A↔C)

---

## ✅ 10. What is Private Service Connect (PSC)?

PSC lets you access Google services using **internal IP** instead of public internet.

---

## ✅ 11. What is Shared VPC?

Shared VPC lets many projects use **one common VPC**.

Used in big companies.

---

## ✅ 12. How to connect GKE to Cloud SQL securely?

Two ways:

1. **Private IP** (best)
2. **Cloud SQL Auth Proxy**

---

## ✅ 13. Internal Load Balancer

Used **inside VPC**. Not visible to internet.

---

## ✅ 14. External Load Balancer

Used to expose services to **public internet**.

---

## ✅ 15. What is a Service Account?

A service account is like a **robot user** for applications.

---

## ✅ 16. What is IAM?

IAM is used to give permissions to:

* Users
* Groups
* Service Accounts

---

## ✅ 17. What is Least Privilege?

Give **minimum required permissions**.

---

## ✅ 18. What is Workload Identity Federation?

Allows GitHub/Jenkins to access GCP **without JSON key files**.

---

## ✅ 19. What is Cloud NAT?

Gives internet access to private resources **safely**.

---

## ✅ 20. Simple GCP Structure

* Project → VPC → Subnets → Firewall → Routes
* IAM → permissions
* SA → for apps/pipelines

---

## ✅ Real-Time Examples for Each Topic

### 1. VPC Example

A company creates a VPC to host their internal applications like HR, Payroll, and Admin tools on a secure private network.

### 2. Subnet Example

Inside the VPC, they create:

* Subnet A → For frontend servers
* Subnet B → For backend servers

### 3. VPC vs Subnet Example

VPC = Whole office
Subnet = Different rooms inside the office

### 4. Firewall Rule Example

Allow only port 80/443 so customers can access your website but block SSH from the internet.

### 5. Firewall Priority Example

* Priority 100 → Allow port 80
* Priority 200 → Deny all
  Since 100 is smaller, port 80 works.

### 6. Route Example

Route tells VM: “To reach the internet, go via the default gateway 0.0.0.0/0”.

### 7. Cloud NAT Example

Your GKE nodes have **no public IP**, but Cloud NAT allows them to download Docker images from the internet.

### 8. Cloud Router Example

Your company’s on-prem network gets a new subnet. Cloud Router learns it automatically using BGP.

### 9. VPC Peering Example

Project A (billing system) needs to connect to Project B (database). VPC Peering allows private communication.

### 10. Private Service Connect Example

GKE calls Cloud SQL using **internal IP** through PSC → no public internet exposed.

### 11. Shared VPC Example

Finance, HR, and Sales projects share a single central VPC managed by the Network team.

### 12. GKE → Cloud SQL Example

Your GKE app connects to Cloud SQL using Private IP. No external IP, no public exposure.

### 13. Internal Load Balancer Example

An internal microservice (payment‑service) is accessible only inside the VPC.

### 14. External Load Balancer Example

Your main website frontend.example.com is publicly available using an external LB.

### 15. Service Account Example

A CI/CD pipeline uses a service account to push Docker images to Artifact Registry.

### 16. IAM Example

You give your teammate **Storage Admin** so he can manage GCS buckets.

### 17. Least Privilege Example

Instead of giving “Editor” role to an app, you give only “Storage Object Viewer”.

### 18. Workload Identity Federation Example

GitHub Actions deploys to GCP **without service account key**, using WIF authentication.

### 19. Cloud NAT Example

Private VM needs to install software from internet → Cloud NAT provides outbound internet access.

### 20. GCP Structure Example

A company uses:

* Project → “prod-app”
* VPC → “prod-network”
* Subnets → frontend, backend
* IAM → roles for dev team
* Service Accounts → CI/CD deploy

If you want, I can create:
✅ Ultra‑simple version (child-level English)
✅ Scenario-based Q&A (very useful for interviews)
✅ One‑page cheat sheet summary

---

## ✅ Real-Time Examples for Each Question (Very Easy to Understand)

### 1. **Difference between VPC and Subnet**

**Example:**
You create a VPC called `production-network`. Inside it, you create two subnets:

* `prod-subnet-1` → for GKE
* `prod-subnet-2` → for Cloud SQL

Just like a **colony (VPC)** contains **streets (subnets)**.

---

### 2. **Firewall Rule Priority**

**Example:**
You create two rules:

* Priority 100 → deny all SSH
* Priority 200 → allow SSH

Priority 100 is lower → so **deny wins** → SSH is blocked.

---

### 3. **Cloud Router Purpose**

**Example:**
You connect your VPC to an on-prem network using VPN.
Cloud Router exchanges routes automatically so both networks know how to reach each other.

---

### 4. **Why NAT Gateway?**

**Example:**
Your backend servers are private (no public IP).
They must download updates from internet.
NAT lets them go **out to internet** without exposing them publicly.

---

### 5. **Shared VPC Architecture**

**Example:**
`network-team` owns the host project.
`dev-team` and `test-team` use the same VPC subnets.
Easier control and centralized firewall management.

---

### 6. **Connect GKE to Cloud SQL Securely**

**Example:**
You create Cloud SQL instance with **Private IP**.
Your GKE cluster is in the same VPC.
GKE pods connect to SQL **without public internet**.

---

### 7. **VPC Peering and Limitations**

**Example:**
You peer VPC-A with VPC-B so both can communicate.
But VPC-A cannot reach VPC-C through B (no transitive peering).

---

### 8. **Private Service Connect Usage**

**Example:**
Your service in VPC publishes an endpoint.
Another team connects privately without exposing public IP.

---

### 9. **How Routes Work Inside VPC**

**Example:**
You create a route:
`0.0.0.0/0 → next-hop: default-internet-gateway`.
This lets all subnets access internet.

---

### 10. **Internal vs External Load Balancer**

**Example:**

* Internal LB → Microservices talk privately inside VPC.
* External LB → Customer hits your website from the internet.

---
