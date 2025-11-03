# ✅ Cloud Logging --- Interview Questions & Answers

## **1. What is Cloud Logging?**

Cloud Logging is a Google Cloud service that **collects, stores,
searches, and analyzes logs** from: - Compute Engine (VMs) - GKE
(Kubernetes) - Cloud Run / Cloud Functions - Load Balancers - VPC Flow
Logs - Cloud SQL - Your custom applications

✅ **Simple Explanation:**\
Cloud Logging helps you understand what is happening inside your Google
Cloud resources by showing their logs.

------------------------------------------------------------------------

## **2. What are Audit Logs?**

Audit logs record **who did what** in your Google Cloud project.

There are 4 types: 1. **Admin Activity Logs** -- When someone
creates/updates/deletes resources\
2. **Data Access Logs** -- When someone reads or writes data\
3. **System Event Logs** -- System-generated events\
4. **Policy Denied Logs** -- When permission is denied

✅ **Simple Explanation:**\
Audit Logs track all actions and access happening inside your GCP
project for security and compliance.

------------------------------------------------------------------------

## **3. Difference between Logs Bucket and Log Sink**

  -----------------------------------------------------------------------
  Feature           Logs Bucket                  Log Sink
  ----------------- ---------------------------- ------------------------
  Purpose           Store logs inside Cloud      Export logs outside
                    Logging                      Cloud Logging

  Storage Target    Logs Bucket                  BigQuery, Cloud Storage,
                                                 Pub/Sub

  Retention         Default 30 days              Based on destination
                    (customizable)               

  Function          Acts as log storage          Routes/export logs to
                                                 other services
  -----------------------------------------------------------------------

✅ **Simple Explanation:**\
- **Logs Bucket** = place where logs are stored\
- **Log Sink** = rule that sends logs to BigQuery, GCS, or Pub/Sub

------------------------------------------------------------------------

## **4. How to See VM Logs?**

### ✅ Method 1 --- Using Cloud Logging (Recommended)

Go to:

    Cloud Console → Logging → Logs Explorer

Filter:

    resource.type="gce_instance"

### ✅ Method 2 --- Inside the VM

Install Ops Agent:

    sudo systemctl status google-cloud-ops-agent

### ✅ Method 3 --- Serial Port Logs

Go to:

    Compute Engine → VM → Serial Port Output

✅ **Simple Explanation:**\
Use **Logs Explorer** with `gce_instance` filter to see VM logs.

------------------------------------------------------------------------

## **5. How to See Pod Logs?**

### ✅ Method 1 --- Cloud Logging UI

Filter:

    resource.type="k8s_container"
    resource.labels.pod_name="your-pod-name"

### ✅ Method 2 --- kubectl (CLI)

    kubectl logs <pod-name> -n <namespace>

✅ **Simple Explanation:**\
Use the "k8s_container" filter in Logs Explorer or run `kubectl logs`.

------------------------------------------------------------------------
