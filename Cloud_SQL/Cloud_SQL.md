# Cloud SQL -- Complete Guide (GCP)

## ✅ Overview

Cloud SQL is a fully managed relational database service for MySQL,
PostgreSQL, and SQL Server on Google Cloud.

## ✅ Key Features

-   Automated backups and point‑in‑time recovery\
-   High availability (regional HA)\
-   Read replicas (regional & cross‑region)\
-   IAM database authentication\
-   Private Service Connect & VPC‑SC support\
-   Automated failover

## ✅ Architecture Diagram (Simple)

    Client → GKE / Cloud Run → Private IP → Cloud SQL Instance → Storage

## ✅ Networking Options

### 1️⃣ Private IP (Recommended)

-   Uses VPC peering\
-   No public exposure\
-   Best for production workloads

### 2️⃣ Public IP

-   Accessible over the internet\
-   Secure using authorized networks / SSL

### 3️⃣ Cloud SQL Auth Proxy

-   Secure socket-based connection\
-   Manages IAM authentication

## ✅ Steps to Create Cloud SQL (MySQL)

### ✅ 1. Go to Cloud SQL Console

`Navigation Menu → SQL → Create Instance → MySQL`

### ✅ 2. Choose Configuration

-   Machine type: e2-medium or better\
-   Storage: SSD, autoscaling enabled\
-   Enable automatic backups\
-   Enable high availability (Regional availability)

### ✅ 3. Networking

-   Select **Private IP**\
-   Choose VPC & allocate private service connection

### ✅ 4. Create User and Database

    CREATE USER 'appuser'@'%' IDENTIFIED BY 'StrongPassword';
    CREATE DATABASE appdb;
    GRANT ALL PRIVILEGES ON appdb.* TO 'appuser'@'%';

## ✅ Connecting from GKE (Private IP)

    cloudsql-proxy --port=3306 asia-south1:project:instance &

Kubernetes deployment example:

``` yaml
env:
  - name: DB_HOST
    value: 10.20.0.5
  - name: DB_USER
    valueFrom:
      secretKeyRef:
        name: sql-secret
        key: username
  - name: DB_PASSWORD
    valueFrom:
      secretKeyRef:
        name: sql-secret
        key: password
```

## ✅ Failover & HA

-   Primary zone failure → automatic failover to standby\
-   Minimal downtime (\< 30 seconds typically)

## ✅ Backup Strategy

-   Automated daily backups\
-   PITR (Point-in-time recovery)\
-   Binary logs enabled

## ✅ Terraform Example

``` hcl
resource "google_sql_database_instance" "default" {
  name             = "my-sql-instance"
  database_version = "MYSQL_8_0"
  region           = "asia-south1"

  settings {
    tier = "db-f1-micro"

    backup_configuration {
      enabled = true
    }

    ip_configuration {
      ipv4_enabled    = false
      private_network = google_compute_network.vpc.self_link
    }
  }
}
```

## ✅ Interview Questions

### ✅ 1. How does Cloud SQL HA work?

Cloud SQL uses synchronous replication to a standby instance in another
zone.

### ✅ 2. Difference between read replica and failover replica?

-   **Read replica**: async replication, for reads\
-   **Failover replica**: sync replication, for HA

### ✅ 3. How do you connect GKE with Cloud SQL privately?

Using Private IP through VPC peering or PSC.

------------------------------------------------------------------------
