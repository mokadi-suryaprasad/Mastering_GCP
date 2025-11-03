# IAMConsole.md — GCP IAM Console Step-by-Step Guide

This document provides a **100% Google Cloud Console UI-based guide** for IAM tasks, Service Accounts, Role Assignment, User Permissions, AND Workload Identity Federation (WIF) restrictions for GitHub Actions.

No CLI commands. **Only Console.** ✅

---

# ✅ 1. IAM Basics (Console Overview)

Google Cloud IAM manages **WHO** (user, service account) can access **WHAT** (resource) and **HOW** (role).

### IAM Identity Types

* **User** → `you@gmail.com`
* **Service Account (SA)** → used by apps, CI/CD
* **Group** → [team@googlegroups.com](mailto:team@googlegroups.com)
* **Workload Identity Pool Identity** → GitHub Actions, AWS, etc.

### IAM Role Types

* **Basic roles** → Viewer, Editor, Owner *(avoid)*
* **Predefined roles** → Storage Admin, GKE Developer
* **Custom roles** → Your own permissions set

---

# ✅ 2. Create a Service Account (Console)

1. Go to **Google Cloud Console**
2. Navigate → **IAM & Admin → Service Accounts**
3. Click **Create Service Account**
4. Fill details:

   * Service Account Name: `github-sa`
   * Description: `Used by GitHub Actions`
5. Click **Create and Continue**
6. Add roles (optional) or skip
7. Click **Done**

Your Service Account is created.

---

# ✅ 3. Assign Roles to a Service Account (Console)

1. Console → **IAM & Admin → IAM**
2. Search for your SA:
   `github-sa@PROJECT_ID.iam.gserviceaccount.com`
3. Click the **pencil icon** ✏️ to edit
4. Click **Add Another Role**
5. Choose roles like:

   * Artifact Registry Writer
   * Cloud Run Admin / GKE Developer (as needed)
6. Click **Save**

---

# ✅ 4. Grant Permissions to a Specific User (Your Email)

Example: `suryaprasa1188@gmail.com`

1. Console → **IAM & Admin → IAM**
2. Click **Grant Access**
3. Enter email: `suryaprasa1188@gmail.com`
4. Choose a role:

   * Viewer
   * Storage Admin
   * Editor *(avoid)*
5. Click **Save**

✅ Now that user has permissions.

---

# ✅ 5. Create Service Account Key (Only If Needed)

> Not recommended. Prefer Workload Identity Federation.

1. Console → **IAM & Admin → Service Accounts**
2. Click your SA
3. Go to **Keys**
4. Click **ADD KEY → Create new key**
5. Choose **JSON** → Download

Store safely.

---

# ✅ 6. Workload Identity Federation (WIF) Setup (Console Only)

This allows GitHub Actions to access Google Cloud **without JSON key files**.

✅ Build — Deploy — Push images — Access GCP from GitHub

---

## ✅ 6.1 Create a Workload Identity Pool

1. Console → **IAM & Admin → Workload Identity Federation**
2. Click **Create Pool**
3. Fill:

   * Pool Name: `github-pool`
   * Description: `GitHub Actions Identity Pool`
4. Click **Create**

Pool created.

---

## ✅ 6.2 Create an OIDC Provider for GitHub

1. Inside the newly created **github-pool**
2. Click **Add Provider**
3. Choose **OIDC Provider**
4. Fill fields:

   * Provider Name: `github-provider`
   * Issuer URL: `https://token.actions.githubusercontent.com`
5. Go to **Attribute Mapping**
6. Add mappings:

   * `google.subject = assertion.sub`
   * `attribute.repository = assertion.repository`
   * `attribute.ref = assertion.ref`
7. Click **Create**

---

## ✅ 6.3 Allow the Provider to Impersonate the Service Account

1. Console → **IAM & Admin → IAM**
2. Search for your SA: `github-sa` → Edit ✏️
3. Under **Principals with access**, click **Add Principal**
4. In **New Principal**, enter:

```
principalSet://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/*
```

5. Add role:

   * **Workload Identity User**
6. Click **Save**

✅ GitHub can now impersonate the service account (but we will restrict it).

---

# ✅ 7. Restrict WIF to a Specific GitHub Repository (Console)

This ensures ONLY a particular GitHub repo can deploy.

1. Console → **IAM & Admin → IAM**
2. Search **github-sa**
3. Click ✏️ edit
4. In the role `Workload Identity User`, click **ADD CONDITION**

### Condition Title

```
GitHub Repository Restriction
```

### Expression

```
attribute.repository == "mokadi-suryaprasad/microservices-demo"
```

5. Click **Save → Save**

✅ Only this repo can access GCP.

---

# ✅ 8. Restrict WIF to a Specific Branch (Console)

Example: Only allow `main` branch.

Repeat the above steps, and in condition use:

```
attribute.ref == "refs/heads/main"
```

✅ Only main branch can deploy.

---

# ✅ 9. Combined Restriction: Repo + Branch (Best Practice)

Use this final combined one:

```
attribute.repository == "mokadi-suryaprasad/microservices-demo" && attribute.ref == "refs/heads/main"
```

✅ Most secure.

---

# ✅ 10. Advanced Examples (Console Conditions)

### Allow multiple branches (main OR dev)

```
attribute.repository == "mokadi-suryaprasad/microservices-demo" && (attribute.ref == "refs/heads/main" || attribute.ref == "refs/heads/dev")
```

### Allow only tag-based deployments

```
attribute.ref.startsWith("refs/tags/")
```

### Allow only pull requests

```
attribute.ref.startsWith("refs/pull/")
```

---

# ✅ 11. Final Best Practices

* Never give **Owner** role to CI/CD
* Prefer **least privilege** roles
* Always restrict WIF by:
  ✅ repo
  ✅ branch
  ✅ environment (optional)
* Avoid service account keys
* Audit IAM changes regularly

---

# ✅ 12. Done!

This file gives **all tasks entirely in GCP Console UI**:
✅ Create SA
✅ Assign roles
✅ Grant user access
✅ WIF setup
✅ WIF conditions (repo/branch)
✅ All Console diagrams explained
