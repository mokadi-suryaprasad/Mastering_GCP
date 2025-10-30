# Google Cloud App Engine — Clear Guide + Real-time Python App Deployment

> This document explains App Engine clearly and gives a **step‑by‑step guide** to deploy a realtime Python (Flask) application to **App Engine (Standard environment)**.

---

## 1 — Quick overview (in simple terms)

**App Engine** is Google Cloud's fully managed Platform-as-a-Service (PaaS). You push your code, and Google runs it for you: it automatically handles servers, scaling, health checks, and basic security. App Engine has two main environments:

* **Standard environment** — sandboxed runtimes for popular languages (fast, cheap, can scale to zero). Great for web apps and APIs that use supported runtimes.
* **Flexible environment** — container-based on Compute Engine VMs (more configurable, supports custom binaries and languages, but costlier and won’t scale to zero).

Use App Engine when you want rapid deployment, built-in autoscaling, easy versioning and traffic splitting, and minimal infra management.

---

## 2 — Key concepts

* **Service**: logical module (e.g., `frontend`, `api`, `worker`). Each service has its own versions.
* **Version**: each deploy creates a version. You can promote a version to receive traffic, or split traffic between versions for canary releases.
* **Instance**: runtime units (sandboxed or VM) that run your code.
* **Handlers**: routing rules in `app.yaml` for static content and request handling.
* **Scaling**: `automatic`, `basic`, or `manual` scaling.

---

## 3 — When to pick Standard vs Flexible

* **Standard**: prefer this for typical Python/Node/Java/Go web apps. Fast deploys, autoscaling to zero, lower cost.
* **Flexible**: pick this when you need custom OS packages, a specific nonstandard language/runtime, or persistent local disk.

---

## 4 — Example realtime Python app (Flask)

We'll deploy a small Flask app that provides a realtime endpoint showing server time and a basic health-check. This is "realtime" in the sense it serves live requests and can be extended (WebSocket-like patterns require extra work; App Engine Standard doesn’t support long-lived WebSockets — for real websockets use Cloud Run or Flexible).

**Project structure**

```
my-flask-app/
├── app.yaml
├── main.py
├── requirements.txt
└── .gcloudignore
```

### `main.py` (Flask app)

```python
from flask import Flask, jsonify, request
import os
import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({
        'message': 'Hello from App Engine (Flask)!',
        'time': datetime.datetime.utcnow().isoformat() + 'Z',
        'env': os.environ.get('GAE_SERVICE', 'unknown')
    })

@app.route('/health')
def health():
    return 'ok', 200

if __name__ == '__main__':
    # local dev server
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)), debug=True)
```

### `requirements.txt`

```
Flask==2.2.5
gunicorn==20.1.0
```

*(Pin versions if you prefer reproducible builds.)*

### `.gcloudignore` (recommended)

```
venv/
__pycache__/
*.pyc
*.pyo
*.log
.env
```

### `app.yaml` (Standard, Python 3 example)

```yaml
runtime: python310
entrypoint: gunicorn -b :$PORT main:app

instance_class: F1  # small instance, optional

automatic_scaling:
  min_instances: 0
  max_instances: 5
  cool_down_period_sec: 90

env_variables:
  ENV: "prod"

handlers:
  - url: /static
    static_dir: static
  - url: /. *
    script: auto
```

> Note: `instance_class` and scaling settings are optional — tune them for cost/performance.

---

## 5 — Step-by-step: Prepare GCP and local environment

> These commands are executed from your local machine.

1. **Install Cloud SDK (gcloud)** if not already installed: [https://cloud.google.com/sdk/docs/install](https://cloud.google.com/sdk/docs/install)

2. **Login and select project**

```bash
gcloud auth login
gcloud config set project PROJECT_ID
```

Replace `PROJECT_ID` with your GCP project ID.

3. **Enable required APIs**

```bash
gcloud services enable appengine.googleapis.com cloudbuild.googleapis.com
```

(If you plan to use Cloud SQL, Artifact Registry, or Secret Manager later, enable those APIs too.)

4. **Create App Engine application (choose region)**

```bash
gcloud app create --region=us-central
```

Pick the region closest to your users. This command runs once per project.

5. **Install Python & virtualenv for local testing**

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py  # test locally on http://localhost:8080
```

---

## 6 — Deploy the app

From the app directory (`my-flask-app/`):

```bash
# Deploy (this will upload and create a new version)
gcloud app deploy app.yaml --quiet

# Open browser to the service
gcloud app browse
```

**What happens**: `gcloud` packages your app, uploads it to App Engine, provisions instances, and makes the new version available. By default the new version is promoted to receive all traffic.

---

## 7 — Verify and manage versions

* List versions:

```bash
gcloud app versions list
```

* If you want to deploy without promoting (create version but don’t route traffic):

```bash
gcloud app deploy --no-promote
```

* Split traffic between versions (canary):

```bash
gcloud app services set-traffic default --splits v1=0.9,v2=0.1
```

* View logs (tail):

```bash
gcloud app logs tail -s default
```

* Read recent logs:

```bash
gcloud app logs read --service=default --limit=100
```

---

## 8 — Environment variables & secrets

### Env variables

Define simple env vars in `app.yaml` under `env_variables` (shown above). For sensitive values use **Secret Manager**.

### Using Secret Manager (recommended for secrets)

1. Create a secret:

```bash
echo -n "my-secret-value" | gcloud secrets create MY_SECRET --data-file=-
```

2. Grant App Engine default service account access:

```bash
# identify service account
GAE_SA=$(gcloud projects get-iam-policy $PROJECT_ID --flatten="bindings[].members" --format="value(bindings.members)" | grep appengine | head -n1)

# grant access (roles/secretmanager.secretAccessor)
gcloud secrets add-iam-policy-binding MY_SECRET \
  --member="serviceAccount:PROJECT_ID@appspot.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

3. Access secret from your code using the Secret Manager client library (or via environment injection in Cloud Build). Example (Python):

```python
from google.cloud import secretmanager

client = secretmanager.SecretManagerServiceClient()
name = f"projects/{PROJECT_ID}/secrets/MY_SECRET/versions/latest"
response = client.access_secret_version(request={"name": name})
secret_value = response.payload.data.decode('UTF-8')
```

(You must `pip install google-cloud-secret-manager` if using the client.)

---

## 9 — Optional: Connect App Engine to Cloud SQL (high-level)

If your realtime app needs a relational DB, use **Cloud SQL**. High-level steps:

1. Create a Cloud SQL instance (MySQL or Postgres) in the same region. Note the instance connection name: `PROJECT:REGION:INSTANCE`.
2. Create database and user.
3. Add Cloud SQL Client role to the App Engine default service account.
4. In your app, use the Unix socket path `/cloudsql/INSTANCE_CONNECTION_NAME` when connecting (or use the Cloud SQL Python connector library).

**Example connection string (MySQL + SQLAlchemy)**

```
unix_socket = '/cloudsql/{INSTANCE_CONNECTION_NAME}'
engine = create_engine(
    'mysql+pymysql://DB_USER:DB_PASS@/DB_NAME',
    connect_args={'unix_socket': unix_socket}
)
```

> Note: For some Cloud SQL setups, you must add `beta_settings: cloud_sql_instances: INSTANCE_CONNECTION_NAME` in `app.yaml` for older docs; current recommended approach is to use the Cloud SQL Python Connector or the unix socket in second gen. Check the Cloud SQL docs for latest guidance.

---

## 10 — CI/CD: Deploy on push using Cloud Build

Add a `cloudbuild.yaml` to run `gcloud app deploy` automatically.

`cloudbuild.yaml`

```yaml
steps:
  - name: 'gcr.io/cloud-builders/gcloud'
    args: ['app', 'deploy', 'app.yaml', '--quiet']
```

Create a Cloud Build trigger connected to your GitHub repo for pushes to `main` (or your branch).

---

## 11 — Cost tips and limits

* Standard environment has a free tier for instance-hours, outgoing bandwidth, and other resources.
* Set `min_instances` to 0 to save cost during idle times.
* Monitor quotas in the Cloud Console.

---

## 12 — Troubleshooting checklist

* `gcloud app deploy` fails: check `app.yaml` syntax and `gcloud` authentication.
* App returns 500: tail logs with `gcloud app logs tail -s default` and check stack traces.
* Database connection issues: verify network/permissions and Cloud SQL instance region.
* Long cold starts: increasing `min_instances` reduces cold starts but increases cost.

---

## 13 — Next steps & enhancements

* Add Cloud Monitoring dashboards and alerting for latency and error rate.
* Use Cloud CDN + Cloud Armor in front of App Engine (where applicable) via Serverless NEG and HTTPS Load Balancer.
* Use VPC Connector to access private resources like Memorystore.
* Consider Cloud Run if you need WebSockets or per-request container flexibility.

---

## 14 — Full copy-ready commands summary (quick)

```bash
# authenticate and set project
gcloud auth login
gcloud config set project PROJECT_ID

# enable apis
gcloud services enable appengine.googleapis.com cloudbuild.googleapis.com

# create app (one-time)
gcloud app create --region=REGION

# deploy
gcloud app deploy app.yaml --quiet

# view logs
gcloud app logs tail -s default

# list versions
gcloud app versions list
```

---

## 15 — Want me to generate this into your repo?

I can create the folder `25-App-Engine/` inside your **Mastering_GCP** repo with:

* `README.md` (this doc)
* Example Flask app files (`main.py`, `requirements.txt`, `app.yaml`, `.gcloudignore`)
* `cloudbuild.yaml` for CI/CD
* Optional `cloudsql` example and sample Terraform to create Cloud SQL

Reply **"generate App Engine module"** and I will add all these files ready to copy-paste.
