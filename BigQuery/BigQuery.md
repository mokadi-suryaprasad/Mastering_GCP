# Google BigQuery

Google BigQuery is a fully managed, serverless, highly scalable data warehouse designed for analytics, reporting, and processing large datasets using SQL. It handles terabytes to petabytes of data without requiring any infrastructure management.

---

## ✅ 1. What is BigQuery?

BigQuery is Google Cloud’s **serverless data warehouse** that allows users to run **fast SQL queries** on massive datasets.  
You focus only on writing queries—Google manages the servers, scaling, and performance tuning.

### ⭐ Key Features
- **Serverless** (no infrastructure to manage)
- **Massive auto-scaling**
- **Real-time analytics support**
- **Columnar storage format**
- **Distributed query engine (Dremel)**
- **Cost-efficient pay-as-you-go model**
- **Integrated with Google Cloud ecosystem**

---

## ✅ 2. BigQuery Core Components

BigQuery follows a hierarchical structure:

```
Project → Dataset → Table → Data
```

### 🔹 Project  
Top-level container in Google Cloud that holds datasets and tables.

### 🔹 Dataset  
A logical grouping of tables.  
Example:  
- `sales_dataset`
- `marketing_dataset`

### 🔹 Table  
A table holds actual data (rows & columns).

### 🔹 Schema  
Defines structure of the table:  
Example:  
- `order_id: INT64`
- `price: FLOAT64`
- `created_at: TIMESTAMP`

### 🔹 Query  
Standard SQL used to read, write, or transform data.

---

## ✅ 3. Storage Types in BigQuery

### 🔸 1. **Native BigQuery Storage**
BigQuery’s internal, optimized columnar storage  
✔ Best performance  
✔ Supports partitioning & clustering

### 🔸 2. **External (Federated) Storage**
Query external data without loading into BigQuery.  
Examples:  
- Google Cloud Storage (CSV, Parquet, JSON)  
- Google Drive  
- Cloud Bigtable  

---

## ✅ 4. Data Ingestion Methods

### 🔹 1. Load Jobs (Batch Load)
Supports: CSV, JSON, Avro, Parquet, ORC  
Efficient & Free for loading.

### 🔹 2. Streaming Inserts
Real-time ingestion using API or Dataflow.

### 🔹 3. Federated Queries
Query external data sources directly.

### 🔹 4. Dataflow / Datastream
For ETL pipelines and real-time replication.

---

## ✅ 5. Partitioning

Partitioning splits a table into smaller segments:

### Types:
- `DAY`
- `HOUR`
- `MONTH`
- `YEAR`
- Integer-based partitioning
- Ingestion-time partitioning

### Benefits:
✔ Faster queries  
✔ Lower cost  
✔ Easy to manage large datasets  

---

## ✅ 6. Clustering

Clustering organizes data based on selected columns.

Example:
```
CLUSTER BY customer_id, country
```

### Benefits:
✔ Faster filtering  
✔ Lower query cost  
✔ Better performance for large tables  

---

## ✅ 7. BigQuery SQL Examples

### 🔹 Select Query
```sql
SELECT * FROM `project.dataset.orders`
WHERE status = "DELIVERED";
```

### 🔹 Create Partitioned + Clustered Table
```sql
CREATE TABLE project.dataset.sales
PARTITION BY DATE(order_time)
CLUSTER BY customer_id AS
SELECT * FROM source_table;
```

### 🔹 Insert Example
```sql
INSERT INTO `project.dataset.users`
(id, name, city)
VALUES (1, "Surya", "Hyderabad");
```

---

## ✅ 8. Export Data from BigQuery

```sql
EXPORT DATA OPTIONS(
  uri='gs://mybucket/export/*.csv',
  format='CSV'
)
AS SELECT * FROM `project.dataset.table`;
```

---

## ✅ 9. BigQuery Pricing (Simple Explanation)

You pay for:

### 🔹 Storage  
Cost for storing data.

### 🔹 Query Processing  
Cost depends on the amount of **data scanned**.

**Formula:**  
```
Query Cost = Scanned Bytes × Pricing
```

Partitioning + clustering reduces scanned data = lower cost.

---

## ✅ 10. Best Practices

✔ Partition large tables  
✔ Cluster frequently filtered columns  
✔ Avoid SELECT *  
✔ Use LIMIT while debugging  
✔ Use table expiry for temporary data  
✔ Use BI Engine for dashboards  
✔ Use materialized views for repeated queries  

---

## ✅ 11. Real-Time Analytics Architecture Example

### 📌 E‑commerce Analytics Pipeline

1. **Website events → Pub/Sub**  
2. **Pub/Sub → Dataflow** (stream processing)  
3. **Dataflow → BigQuery** (real-time ingestion)  
4. **BigQuery → Looker Studio** (dashboards)

### Use Cases:
- Real-time sales dashboard  
- Order monitoring  
- User behavior analytics  
- Add-to-cart analysis  

---

## ✅ 12. BigQuery Interview Questions

### 🔹 What is BigQuery?
A serverless, distributed SQL-based data warehouse.

### 🔹 Difference between Dataset and Table?
- Dataset → container  
- Table → actual data  

### 🔹 What is Partitioning?
Dividing data into segments for faster queries and lower costs.

### 🔹 What is Clustering?
Sorting and grouping data by columns to reduce scanned data.

### 🔹 How to reduce cost?
- Partition & cluster  
- Avoid SELECT *  
- Use filters  
- Use materialized views  

### 🔹 What is a Federated Query?
Querying external data without loading it into BigQuery.

---

## ✅ 13. Easy Summary

- BigQuery = Google’s fastest analytics platform  
- Fully serverless → no maintenance  
- SQL-based, easy to learn  
- Best for TB to PB data  
- Partition + cluster = fast + cheap  

---

This document gives a complete end‑to‑end understanding of all BigQuery concepts.
