# Real-Time E-commerce Analytics Pipeline – BigQuery_Project.md

This document explains **step by step** how to build a **real-time analytics pipeline** on Google Cloud using:

- **Pub/Sub** – for streaming website events  
- **Dataflow (Apache Beam)** – for processing events in real time  
- **BigQuery** – for storing and querying analytics data  
- **Looker Studio** – for dashboard and reports  

Architecture:

```text
Website / App  →  Pub/Sub Topic  →  Dataflow Streaming Job  →  BigQuery Table  →  Looker Studio
```

---

## 1. Prerequisites

Before starting, make sure you have:

1. A **Google Cloud account** and **billing enabled**.
2. A **GCP Project** (example: `ecommerce-analytics-demo`).
3. **Roles / Permissions** (or equivalent):
   - Pub/Sub Admin / Editor
   - Dataflow Developer
   - BigQuery Admin (or Data Editor)
   - Storage Admin (for Dataflow temporary files)
4. **Tools Installed (optional but recommended):**
   - `gcloud` CLI
   - `bq` CLI
   - `python` (if you want to simulate events using a script)

You can also do everything via the **Google Cloud Console** (web UI).

---

## 2. Enable Required APIs

You must enable the following APIs for your project:

- Cloud Pub/Sub API  
- Dataflow API  
- BigQuery API  
- Cloud Storage API (for Dataflow temp files)

Using CLI:

```bash
gcloud services enable \
  pubsub.googleapis.com \
  dataflow.googleapis.com \
  bigquery.googleapis.com \
  storage.googleapis.com \
  monitoring.googleapis.com
```

Or enable each API from **APIs & Services → Library** in the console.

---

## 3. Create a Pub/Sub Topic for Website Events

### 3.1 Create Topic

Example topic name: `website-events-topic`

**Using Console:**
1. Go to **Pub/Sub → Topics**.
2. Click **Create topic**.
3. Topic ID: `website-events-topic`
4. Keep defaults and click **Create**.

**Using CLI:**
```bash
gcloud pubsub topics create website-events-topic
```

### 3.2 Create a Subscription (optional but useful)

Subscription is needed if you want to debug or read messages directly.

Example subscription name: `website-events-sub`

```bash
gcloud pubsub subscriptions create website-events-sub \
  --topic=website-events-topic
```

---

## 4. Define Your Event Schema

Decide what data you want to capture from your e-commerce website. For example:

- `event_id` – unique ID for the event  
- `event_type` – e.g., `page_view`, `add_to_cart`, `purchase`  
- `user_id` – user identifier  
- `session_id` – session identifier  
- `product_id` – product identifier  
- `price` – price of product  
- `currency` – e.g., `INR`, `USD`  
- `timestamp` – event time (UTC)

Example JSON event:

```json
{
  "event_id": "evt_12345",
  "event_type": "purchase",
  "user_id": "user_001",
  "session_id": "sess_abc",
  "product_id": "prod_99",
  "price": 1499.50,
  "currency": "INR",
  "timestamp": "2025-11-27T10:25:00Z"
}
```

All events sent to Pub/Sub should follow this schema.

---

## 5. Create a BigQuery Dataset & Table

### 5.1 Create Dataset

Dataset name example: `ecommerce_analytics`

**Using Console:**
1. Go to **BigQuery** in the Cloud Console.
2. Click on your project → **Create dataset**.
3. Dataset ID: `ecommerce_analytics`
4. Data location: choose (e.g., `asia-south1` or `US`).
5. Click **Create dataset**.

**Using CLI:**
```bash
bq --location=asia-south1 mk \
  --dataset \
  your-project-id:ecommerce_analytics
```

### 5.2 Create Table for Streaming Data

Table name example: `events_streaming`

**Recommended:**  
- Use **ingestion-time partitioning** on `_PARTITIONTIME` or  
- Use a **TIMESTAMP** column (`timestamp`) and partition on it.

**Schema:**
- `event_id: STRING`
- `event_type: STRING`
- `user_id: STRING`
- `session_id: STRING`
- `product_id: STRING`
- `price: FLOAT64`
- `currency: STRING`
- `timestamp: TIMESTAMP`

Using CLI:

```bash
bq mk \
  --table \
  --schema event_id:STRING,event_type:STRING,user_id:STRING,session_id:STRING,product_id:STRING,price:FLOAT64,currency:STRING,timestamp:TIMESTAMP \
  --time_partitioning_type=DAY \
  your-project-id:ecommerce_analytics.events_streaming
```

Or use the BigQuery Console → **Create table** → choose **Empty table**, set schema manually, and enable **Partitioning**.

---

## 6. Create a Cloud Storage Bucket for Dataflow

Dataflow needs a GCS bucket for **staging** and **temporary** files.

Bucket name example: `df-ecom-temp-yourname`

```bash
gsutil mb -l asia-south1 gs://df-ecom-temp-yourname
```

You will reference this bucket when creating the Dataflow job.

---

## 7. Build the Dataflow Streaming Pipeline

You have two options:

1. Use **Google-provided template**: Pub/Sub → BigQuery.  
2. Create a **custom Apache Beam pipeline** in Java or Python.

### 7.1 Option 1 – Use Pub/Sub to BigQuery Template (Recommended for beginners)

This is the easiest way.

**Steps (Console):**
1. Go to **Dataflow → Jobs**.
2. Click **Create job from template**.
3. Job name: `realtime-ecom-events-job`
4. Region: choose (e.g., `asia-south1`).
5. Template: `Pub/Sub subscription to BigQuery` (or similar, depending on UI).  
6. Parameters (important):
   - **Input Pub/Sub subscription**: `projects/your-project-id/subscriptions/website-events-sub`
   - **Output table**: `your-project-id:ecommerce_analytics.events_streaming`
   - **Temporary location**: `gs://df-ecom-temp-yourname/temp`
7. Click **Run job**.

Dataflow will now continuously read messages from Pub/Sub and write them into BigQuery.

### 7.2 Option 2 – Custom Apache Beam Pipeline (Python example – high level)

If you want more control (e.g., transformations, filtering), you can create a Python script:

```python
import json
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions, StandardOptions

class ParseEvent(beam.DoFn):
    def process(self, element):
        record = json.loads(element)
        yield {
            "event_id": record.get("event_id"),
            "event_type": record.get("event_type"),
            "user_id": record.get("user_id"),
            "session_id": record.get("session_id"),
            "product_id": record.get("product_id"),
            "price": float(record.get("price", 0)),
            "currency": record.get("currency"),
            "timestamp": record.get("timestamp")
        }

def run():
    options = PipelineOptions(
        streaming=True,
        save_main_session=True,
        project="your-project-id",
        region="asia-south1",
        temp_location="gs://df-ecom-temp-yourname/temp"
    )
    options.view_as(StandardOptions).streaming = True

    with beam.Pipeline(options=options) as p:
        (
            p
            | "Read from Pub/Sub" >> beam.io.ReadFromPubSub(
                subscription="projects/your-project-id/subscriptions/website-events-sub"
            )
            | "Parse JSON" >> beam.ParDo(ParseEvent())
            | "Write to BigQuery" >> beam.io.WriteToBigQuery(
                table="your-project-id:ecommerce_analytics.events_streaming",
                write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
                create_disposition=beam.io.BigQueryDisposition.CREATE_NEVER
            )
        )

if __name__ == "__main__":
    run()
```

Then you would **submit this as a Dataflow job**.

---

## 8. Simulate Website Events (Producer)

To test your pipeline, you can simulate events from your local machine or from a Cloud Function.

### 8.1 Python Script to Publish Sample Events to Pub/Sub

```python
import json
import time
from google.cloud import pubsub_v1

project_id = "your-project-id"
topic_id = "website-events-topic"

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_id)

def publish_event():
    import random, uuid, datetime

    event = {
        "event_id": str(uuid.uuid4()),
        "event_type": random.choice(["page_view", "add_to_cart", "purchase"]),
        "user_id": f"user_{random.randint(1, 100)}",
        "session_id": f"sess_{random.randint(1, 50)}",
        "product_id": f"prod_{random.randint(1, 20)}",
        "price": round(random.uniform(100.0, 5000.0), 2),
        "currency": "INR",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
    }

    data = json.dumps(event).encode("utf-8")
    future = publisher.publish(topic_path, data=data)
    print(f"Published event: {event['event_id']}")

if __name__ == "__main__":
    while True:
        publish_event()
        time.sleep(2)  # send an event every 2 seconds
```

Run the script and verify events are flowing into Pub/Sub.

---

## 9. Verify Data in BigQuery

1. Go to **BigQuery** console.  
2. Open dataset: `ecommerce_analytics`.  
3. Click on table: `events_streaming`.  
4. Click **Preview** → you should see new rows coming in.  
5. You can also run SQL:

```sql
SELECT
  event_type,
  COUNT(*) AS total_events
FROM
  `your-project-id.ecommerce_analytics.events_streaming`
GROUP BY
  event_type;
```

Or check sales:

```sql
SELECT
  DATE(timestamp) AS event_date,
  SUM(price) AS total_revenue,
  COUNTIF(event_type = 'purchase') AS total_orders
FROM
  `your-project-id.ecommerce_analytics.events_streaming`
GROUP BY
  event_date
ORDER BY
  event_date DESC;
```

---

## 10. Create Looker Studio Dashboard

Now you will create a **real-time dashboard**.

1. Go to **Looker Studio** (formerly Data Studio).  
2. Click **Blank report**.  
3. For **data source**, choose **BigQuery**.  
4. Select:
   - Project: `your-project-id`
   - Dataset: `ecommerce_analytics`
   - Table: `events_streaming`
5. Click **Add** → **Add to report**.

Now you can create charts:

- **Time series chart** for revenue by time:
  - Dimension: `timestamp` (or `DATETIME(timestamp)`)
  - Metric: Sum of `price`
- **Bar chart** for event counts by `event_type`:
  - Dimension: `event_type`
  - Metric: `Record count`
- **Scorecards** for:
  - Total revenue today
  - Total orders today
  - Active users (approx from distinct `user_id`)

Looker Studio will continuously query BigQuery, so as events keep streaming, your dashboard will update (near real time).

---

## 11. Use Cases of This Pipeline

This real-time pipeline can be used for:

- **Sales monitoring** (current revenue, orders per minute/hour).  
- **User behavior analytics** (page views, add-to-cart trends).  
- **Product performance** (top products by revenue).  
- **Marketing performance** (if you add source/medium fields).  

You can extend it by adding:

- Window-based aggregations in Dataflow.  
- Alerts using Cloud Monitoring.  
- Exporting aggregates to other systems.

---

## 12. Cleanup (To Avoid Extra Costs)

When you are done testing:

1. **Stop the Dataflow job** (cancel it from Dataflow console).  
2. Delete or pause the **event producer script**.  
3. Delete the **Pub/Sub topic** and **subscription** if not needed:  

   ```bash
   gcloud pubsub subscriptions delete website-events-sub
   gcloud pubsub topics delete website-events-topic
   ```

4. Delete **BigQuery tables** or dataset if not needed:

   ```bash
   bq rm -t your-project-id:ecommerce_analytics.events_streaming
   bq rm -r -f your-project-id:ecommerce_analytics
   ```

5. Delete **GCS bucket** (if only used for this demo):

   ```bash
   gsutil rm -r gs://df-ecom-temp-yourname
   ```

---

You now have a complete **Real-Time E-commerce Analytics Pipeline** design using:

- Pub/Sub (events)  
- Dataflow (stream processing)  
- BigQuery (analytics)  
- Looker Studio (dashboards)

You can reuse this pattern for many real-time analytics use cases.
