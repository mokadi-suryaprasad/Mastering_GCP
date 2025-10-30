# Google App Engine -- Features Overview

## 1. Fully Managed Serverless Platform

Google App Engine lets you deploy applications without managing servers,
VMs, clusters, or infrastructure. Google automatically handles scaling,
security patches, networking, and load balancing.

## 2. Two Deployment Environments

### Standard Environment

-   Fast startup time
-   Auto-scales to zero
-   Low cost
-   Language-specific sandboxes

### Flexible Environment

-   Runs on Compute Engine VMs
-   Supports custom Docker containers
-   Full OS access
-   Ideal for complex workloads

## 3. Services

App Engine apps are divided into services (microservices).\
Examples: - default (mandatory) - api-service - auth-service -
payment-service

Each service can have independent scaling and versions.

## 4. Versions

Every deployment creates a version.\
You can: - Rollback instantly\
- Split traffic between versions\
- Keep multiple environments

## 5. Instances

Instances are the actual running containers or VMs that serve requests.\
Standard → sandbox instances\
Flexible → Compute Engine instances

## 6. Scaling Options

### Automatic Scaling

Best for production workloads --- auto adjusts capacity.

### Basic Scaling

Starts when requests arrive and shuts down when idle.

### Manual Scaling

Keeps a fixed number of instances running.

## 7. Traffic Splitting

App Engine supports: - Blue/Green deployments\
- Canary releases\
- A/B testing

Example: - v1 → 80% - v2 → 20%

## 8. app.yaml Configuration

Defines: - Runtime - Scaling rules - Environment variables -
Entrypoint - Instance class

## 9. App Engine Built-in Features

-   Cron jobs
-   Task queues
-   Memcache
-   Firewall rules
-   Secret Manager integration
-   Cloud Logging & Monitoring
-   Admin API for automation

## 10. Security Features

-   HTTPS by default\
-   IAM permissions\
-   Identity-Aware Proxy (IAP)\
-   Private IP to Cloud SQL\
-   VPC Access Connector

## 11. Networking Features

-   VPC connectors\
-   Egress control\
-   Private Cloud SQL\
-   Load balancing

## 12. Deployment Commands

Deploy:

    gcloud app deploy

List services:

    gcloud app services list

List versions:

    gcloud app versions list

Delete version:

    gcloud app versions delete VERSION_ID

## 13. Standard vs Flexible Comparison

  Feature          Standard   Flexible
  ---------------- ---------- ----------
  Startup          Fast       Slow
  Scaling          Instant    VM-based
  OS               Sandbox    Linux VM
  Docker           No         Yes
  Cost             Cheaper    Higher
  Custom Runtime   No         Yes

## 14. Use Cases

-   Web applications\
-   APIs\
-   Internal company apps\
-   Cron-driven tasks\
-   Low-maintenance workloads

## 15. Limitations

-   Cannot delete the default service\
-   Standard environment has OS restrictions\
-   Not ideal for heavy compute workloads

## 16. Alternatives

-   Cloud Run\
-   Cloud Functions\
-   GKE (Kubernetes)
