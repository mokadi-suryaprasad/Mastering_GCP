# Cloud Run

## What is Cloud Run?

Google Cloud Run is a service that lets you run your applications in
*containers* without managing servers. You only provide your code inside
a container, and Cloud Run takes care of running it for you.

## Why Cloud Run?

-   No servers to manage\
-   Automatically scales up when traffic increases\
-   Scales down to zero when no one is using it\
-   Very fast and easy to deploy\
-   Pay only when your service is running

## How it works

1.  You create a Docker container for your app\
2.  You push the container to Google Artifact Registry\
3.  You deploy the container on Cloud Run\
4.  Cloud Run gives you a public URL

## Benefits

-   Supports any language (Python, Java, Go, Node.js, etc.)\
-   Very cheap because it scales to zero\
-   Secure by default\
-   Works well for APIs, microservices, and background tasks

## Example Use Cases

-   REST API services\
-   Webhooks\
-   Backend microservices\
-   Scheduled jobs (with Cloud Scheduler)\
-   Lightweight websites


✅ Cloud Run vs App Engine vs GKE — Comparison Diagram

``` text
                          ┌──────────────────────────────┐
                          │      Google Cloud Compute     │
                          └──────────────────────────────┘
                                      │
        ┌─────────────────────────────┼────────────────────────────────┐
        │                             │                                │
┌──────────────────┐        ┌──────────────────┐             ┌──────────────────┐
│    Cloud Run     │        │   App Engine     │             │       GKE         │
│  (Serverless)    │        │ (PaaS Platform)  │             │ (Kubernetes)      │
└──────────────────┘        └──────────────────┘             └──────────────────┘
        │                             │                                │
        │                             │                                │
        ▼                             ▼                                ▼

  • Fully managed                • Fully managed                  • Fully managed control plane
  • Run containers               • Deploy code (no infra)         • You manage nodes & clusters
  • Scales to zero               • Scales automatically           • Highly customizable
  • Event-driven apps            • Best for web apps/APIs         • Best for microservices at scale
  • Great for microservices      • Supports runtimes only         • Needs DevOps expertise

        ▲                             ▲                                ▲
        │                             │                                │
        └─────────────── Use Cases & Limitations Comparison ───────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                           High-Level Comparison                             │
├──────────────────────┬───────────────────────┬──────────────────────────────┤
│ Feature              │ Cloud Run             │ App Engine                  │ GKE
├──────────────────────┼───────────────────────┼──────────────────────────────┤
│ Deploy Type          │ Container              │ Code / Containers            │ Pods/Deployments
│ Scaling              │ Auto → Zero            │ Auto (No zero)               │ Manual/Auto
│ Traffic Splitting    │ Yes                    │ Yes                          │ Yes
│ Customization Level  │ Medium                 │ Low                          │ Very High
│ Pricing              │ Per-request            │ Instance-based               │ Node-based
│ Best For             │ Microservices, APIs    │ Web apps, simple APIs        │ Large-scale systems
│ Control over Infra   │ Low                    │ Very Low                     │ High
│ Cold Starts          │ Sometimes              │ Minimal                      │ None (always running)
└──────────────────────┴───────────────────────┴──────────────────────────────┘

```
✅ Comparison: Cloud Run vs App Engine vs GKE

| Feature                 | **Cloud Run**          | **App Engine**                     | **GKE (Kubernetes)**                    |
| ----------------------- | ---------------------- | ---------------------------------- | --------------------------------------- |
| **Compute Type**        | Serverless containers  | Serverless apps (runtime-based)    | Kubernetes cluster (VMs)                |
| **Scaling**             | Auto-scale to **zero** | Auto-scale to zero (only standard) | Auto-scale but **never to zero**        |
| **Pricing**             | Pay per request/time   | Pay per request or instance        | Pay for nodes always                    |
| **Deployment**          | Deploy container       | Deploy code (Java, Python, Node…)  | Deploy pods, deployments, YAML          |
| **Flexibility**         | Any language/runtime   | Only supported runtimes            | Any workload, full control              |
| **Operations**          | Very low ops           | Very low ops                       | High ops (cluster mgmt)                 |
| **Best for**            | Microservices, APIs    | Web apps, monoliths                | Large-scale apps, multi-service systems |
| **Traffic splitting**   | ✅ Yes                  | ✅ Yes                              | ✅ Yes                                   |
| **Custom domains**      | ✅ Yes                  | ✅ Yes                              | ✅ Yes                                   |
| **Max request timeout** | 60 minutes             | 60 minutes                         | No limit                                |
| **Autoscaling speed**   | Very fast              | Fast                               | Slow–medium                             |

✅ Cloud Run – Limitations

| Limitation                              | Cloud Run                          |
| --------------------------------------- | ---------------------------------- |
| **Request timeout**                     | 60 minutes                         |
| **No containers requiring root access** | ❌ Not allowed                      |
| **No stateful apps**                    | Must use Firestore, Cloud SQL, GCS |
| **Max container max CPU/memory**        | 4 CPU, 16 GB RAM (as of now)       |
| **WebSockets**                          | ✅ Supported                        |
| **TCP/UDP**                             | ❌ Not supported (HTTP only)        |
| **Background jobs**                     | ✅ Cloud Run Jobs, not Services     |


✅ App Engine – Limitations

| Limitation                            | App Engine                   |
| ------------------------------------- | ---------------------------- |
| **Locked runtimes**                   | Only supported languages     |
| **Slow startup on Flex**              | Flex uses VMs                |
| **No Docker control (Standard)**      | Cannot use custom base image |
| **Traffic splitting only by version** | Not by header/path           |
| **Less popular now**                  | Being replaced by Cloud Run  |


✅ GKE – Limitations

| Limitation                      | GKE                                     |
| ------------------------------- | --------------------------------------- |
| **Complex operations**          | Needs cluster management                |
| **Cost does not scale to zero** | At least 1–3 nodes always running       |
| **Upgrades must be managed**    | Node upgrades, security patches         |
| **Learning curve**              | YAML, deployments, services, networking |


## Simple Definition

Cloud Run is a serverless service that runs your containerized
applications automatically with no servers and no manual scaling.
