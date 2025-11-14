
## 🏦 Restricting Payroll Bucket Access in GCP
This document explains two secure methods to restrict access to a Payroll bucket in Google Cloud Storage (GCS).  
Bucket name: **payroll-team-bucket**

---

# ✅ Method 1: Restrict Bucket Access Using IAM

## Step 1 – Open the Bucket
1. Go to Google Cloud Console  
2. Navigate to Cloud Storage → Buckets  
3. Click on **payroll-team-bucket**

## Step 2 – Enable Uniform Bucket-Level Access
1. Go to Permissions / Protection tab  
2. Turn ON **Uniform bucket-level access**

## Step 3 – Remove Unwanted Access
Remove:
- allUsers  
- allAuthenticatedUsers  
- Any non-payroll users

## Step 4 – Grant Access Only to Payroll Team
Add group:
**payroll@yourcompany.com**

Assign role:
- Storage Object Viewer (read-only)
- Storage Object Admin (read + write)

## Step 5 – Verify
- Payroll member → access works  
- Non-payroll member → access denied  

---

# 🛡️ Method 2: Restrict Bucket Using Principal Access Boundary (PAB)

## What is PAB?
A Principal Access Boundary sets the *maximum permissions* a user/service account can have, even if they are given higher roles accidentally.

## Step 1 – Open PAB
Console → IAM & Admin → Principal Access Boundaries → Create

## Step 2 – Choose Principal
Example:  
`payroll@yourcompany.com` (group)  
or service account

## Step 3 – Select Allowed Resource
```
projects/_/buckets/payroll-team-bucket
```

## Step 4 – Select Allowed Permissions
Examples:
- storage.objects.get  
- storage.objects.list  
- storage.objects.create

## Step 5 – Save and Apply Boundary

## Testing
- Access OTHER bucket → Access Denied  
- Access payroll bucket → Allowed  

---

# 🎉 Summary
| Method | Function | Best For |
|--------|----------|----------|
| IAM | Restrict bucket to payroll team | Common usage |
| PAB | Hard restrict max permissions | High security |
