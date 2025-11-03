# GCP IAM — One Complete Step-by-Step Guide

This single file provides a **step-by-step** runnable guide for common IAM tasks and Workload Identity Federation (WIF) setups.

> Replace `PROJECT_ID`, `PROJECT_NUMBER`, `REGION`, `SERVICE_ACCOUNT_NAME`, and other placeholders with your values.

---

## Step 0 — Prerequisites

1. Install and initialize Cloud SDK (gcloud).

   ```bash
   gcloud init
   gcloud auth login
   gcloud config set project PROJECT_ID
   ```
2. Ensure you have **Owner** or **IAM Admin** rights on the project.
3. Optional: Install kubectl, Terraform, and GitHub CLI if required.

---

## Step 1 — Quick IAM Concepts (1-min)

* **Identity**: `user:you@gmail.com`, `serviceAccount:sa@PROJECT_ID.iam.gserviceaccount.com`, `group:team@googlegroups.com`.
* **Role**: `roles/viewer`, `roles/storage.admin`, `roles/container.admin`.
* **Resource**: project, bucket, cluster, dataset.

---

## Step 2 — Create a Service Account (UI + CLI)

### UI (Console)

1. Console → **IAM & Admin → Service Accounts** → **Create Service Account**.
2. Provide name and ID → **Create**.
3. Attach roles now or later → **Done**.

### CLI

```bash
gcloud iam service-accounts create SERVICE_ACCOUNT_NAME \
  --display-name="My SA for CI/CD"
```

Confirm:

```bash
gcloud iam service-accounts list --filter="SERVICE_ACCOUNT_NAME"
```

---

## Step 3 — Assign Roles to a Service Account

### Use principle of least privilege. Assign only necessary roles.

### CLI example (Storage + Artifact Registry push):

```bash
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:SERVICE_ACCOUNT_NAME@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:SERVICE_ACCOUNT_NAME@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"
```

### Console: IAM → find SA → Edit principal → Add role → Save

---

## Step 4 — Grant a Specific User Access (Your email)

Grant to `suryaprasa1188@gmail.com` as example.

### Viewer role (CLI):

```bash
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="user:suryaprasa1188@gmail.com" \
  --role="roles/viewer"
```

### Console: IAM → Grant Access → Enter email → Select role → Save

---

## Step 5 — Create & Download a Service Account Key (Only if necessary)

> Use keys only when external tools can't use WIF.

### Console:

IAM → Service Accounts → Select SA → Keys → Add Key → Create new key → JSON

### CLI:

```bash
gcloud iam service-accounts keys create key.json \
  --iam-account=SERVICE_ACCOUNT_NAME@PROJECT_ID.iam.gserviceaccount.com
```

Store `key.json` securely. Rotate and delete when not needed.

---

## Step 6 — Use Service Account (Example: gcloud auth)

```bash
# Using key.json
gcloud auth activate-service-account --key-file=key.json
# Then run gcloud commands
gcloud auth list
```

---

## Step 7 — Best Practices & Hardening Checklist

* Use predefined roles, not Owner/Editor.
* Use Groups to assign team access.
* Prefer Workload Identity Federation over JSON keys.
* Restrict SA impersonation using `roles/iam.workloadIdentityUser` to a specific pool/provider.
* Enable Cloud Audit Logs for IAM changes.
* Rotate keys and remove unused SAs.

---

## Step 8 — Workload Identity Federation (WIF) — Full Setup for GitHub Actions (No JSON keys)

This creates a WIF pool, provider, SA, binds the pool to the SA, and shows a GitHub Actions workflow snippet.

### 8.1 Create a Workload Identity Pool

```bash
gcloud iam workload-identity-pools create github-pool \
  --location="global" \
  --display-name="GitHub Actions Pool"
```

Get the pool resource name (used later):

```bash
gcloud iam workload-identity-pools describe github-pool --location="global" --format="value(name)"
```

### 8.2 Create an OIDC Provider for GitHub

```bash
gcloud iam workload-identity-pools providers create-oidc github-provider \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --display-name="GitHub Provider" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository,attribute.ref=assertion.ref"
```

### 8.3 Create the Service Account for GitHub

```bash
gcloud iam service-accounts create github-sa --display-name="GitHub deploy SA"
```

### 8.4 Allow the WIF pool to impersonate the Service Account

Replace `PROJECT_NUMBER` with your project's number.

```bash
gcloud iam service-accounts add-iam-policy-binding \
  github-sa@PROJECT_ID.iam.gserviceaccount.com \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/*"
```

### 8.5 Grant required roles to the Service Account

Example: GKE deploy + Artifact Registry push

```bash
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:github-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/container.developer"

gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:github-sa@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"
```

### 8.6 (Optional) Restrict provider to a single GitHub repository and branch

You can create an IAM condition on the SA binding so only a specific repository and branch can impersonate:

```bash
# Example condition (pseudo-syntax) - set via console or IAM policy update with condition
# Condition: attribute.repository == "your-org/your-repo" && attribute.ref == "refs/heads/main"
```

### 8.7 GitHub Actions workflow example (auth step)

```yaml
permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - id: auth
        uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: "projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/providers/github-provider"
          service_account: "github-sa@PROJECT_ID.iam.gserviceaccount.com"

      - name: Configure Docker
        run: gcloud auth configure-docker REGION-docker.pkg.dev

      - name: Deploy to GKE
        run: |
          gcloud container clusters get-credentials mycluster --region REGION
          kubectl apply -f k8s/
```

---

## Step 9 — Terraform example: Grant a user and create SA

```hcl
resource "google_service_account" "ci_sa" {
  account_id   = "ci-sa"
  display_name = "CI Service Account"
}

resource "google_project_iam_member" "user_viewer" {
  project = "PROJECT_ID"
  role    = "roles/viewer"
  member  = "user:suryaprasa1188@gmail.com"
}

resource "google_project_iam_member" "sa_storage" {
  project = "PROJECT_ID"
  role    = "roles/storage.admin"
  member  = "serviceAccount:${google_service_account.ci_sa.email}"
}
```

---

## Step 10 — Troubleshooting Tips

* `permission denied` → check role and resource scope (project vs org vs folder).
* `gcloud projects add-iam-policy-binding` fails → ensure you have `resourcemanager.projects.getIamPolicy` permission.
* WIF not working in GitHub → ensure `id-token: write` permission and provider ARN are correct.

---

## Final Notes

This single document contains all necessary one-command steps for:

* Creating and managing service accounts
* Assigning roles to users and SAs
* Creating keys (when unavoidable)
* Best practices
* Full Workload Identity Federation setup with GitHub Actions

If you want, I can now:

* Add diagrams (Mermaid)
* Narrow the guide to a specific use-case (GKE deploy, Cloud Run)
* Add repository/branch restriction examples for WIF
