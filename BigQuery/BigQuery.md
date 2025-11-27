# ✅ Google BigQuery

Google BigQuery is a **fully managed, serverless data warehouse** used for analytics, reporting, and large‑scale SQL queries.

---

# ✅ 1. What is BigQuery?

BigQuery is a **serverless data warehouse** that allows you to run **fast SQL queries** on large datasets (TB–PB scale) without managing servers.

### ✅ Key Features
- No servers or clusters to manage  
- Auto-scaling  
- Real-time analytics  
- Low cost using pay‑as‑you‑go  
- Extremely fast queries using columnar storage + Dremel engine  

---

# ✅ 2. BigQuery Core Components

### ✅ **1. Project**  
Container for datasets.

### ✅ **2. Dataset**  
Logical grouping of tables.  
Example:  
`retail_dataset`, `orders_dataset`

### ✅ **3. Table**  
Stores data in rows & columns (like SQL table).

### ✅ **4. Schema**  
Defines column names + types  
Example:  
`order_id: INT64`, `price: FLOAT`, `created_at: TIMESTAMP`

### ✅ **5. Query**  
Standard SQL.

---

# ✅ 3. Storage Types in BigQuery

### ✅ 1. **Native Storage**  
BigQuery internal storage.

### ✅ 2. **External Storage**  
Query data without loading into BigQuery.  
Sources:
- Cloud Storage  
- Google Drive  
- Cloud Bigtable  

Example: Query CSV from GCS directly.

---

# ✅ 4. Ingestion Methods

### ✅ 1. Load jobs  
Upload files (CSV, JSON, Parquet, ORC, Avro).

### ✅ 2. Streaming inserts  
Real-time ingestion using API.  
Example: e-commerce events streaming.

### ✅ 3. Federated queries  
Query external sources.

### ✅ 4. Dataflow / Datastream pipeline  
ETL pipelines.

---

# ✅ 5. Partitioning in BigQuery

Partitioning improves speed + reduces cost.

### ✅ Types of Partitioning:
- **Time-based partitioning** (DAY, HOUR, MONTH)
- **Integer partitioning**
- **Ingestion-time partitioning**

✅ Helps reduce scanned TBs → query cost drops.

---

# ✅ 6. Clustering

Organizes data based on selected columns.

Example:
`CLUSTER BY user_id, country`

✅ Fast query results  
✅ Lower cost by scanning fewer blocks

---

# ✅ 7. BigQuery SQL Examples

### ✅ Select
```sql
SELECT * FROM `project.dataset.orders`
WHERE status = "DELIVERED";
```

### ✅ Partition + Cluster Table
```sql
CREATE TABLE project.dataset.sales
PARTITION BY DATE(order_time)
CLUSTER BY customer_id AS
SELECT * FROM source_table;
```

### ✅ Insert
```sql
INSERT INTO `project.dataset.users`
(id, name, city)
VALUES (1, "Surya", "Hyderabad");
```

---

# ✅ 8. Export Data from BigQuery

Export table to GCS:

```sql
EXPORT DATA OPTIONS(
  uri='gs://mybucket/export/*.csv',
  format='CSV'
)
AS SELECT * FROM `project.dataset.table`;
```

---

# ✅ 9. BigQuery Pricing (Simple Explanation)

You pay for:
1. **Storage** (how much data stored)
2. **Query Processing** (amount of data scanned)

✅ **Query cost = Scanned Bytes × Pricing**  
✅ Partition + Cluster ⇒ reduces scanned TB ⇒ saves cost

---

# ✅ 10. BigQuery Best Practices

✅ Use **partitioning & clustering**  
✅ Select only required columns  
✅ Avoid SELECT * in production  
✅ Use table expiration policies  
✅ Keep staging tables separate  
✅ Use BI Engine for Looker/Tableau  

---

# ✅ 11. Real-time Architecture Example  

### 📌 Example: E-commerce analytics pipeline  
1. Website events → Pub/Sub  
2. Pub/Sub → Dataflow  
3. Dataflow → BigQuery (streaming)  
4. BigQuery → Looker Studio dashboards  

✅ Used for sales, orders, user behavior insights.

---

# ✅ 12. Interview Questions

### ✅ 1. What is BigQuery?  
A serverless data warehouse used for analytics with SQL.

### ✅ 2. Difference between Dataset & Table?  
Dataset = container,  
Table = data inside it.

### ✅ 3. What is partitioning?  
Breaking data into small sections (DAY/HOUR) for faster + cheaper queries.

### ✅ 4. What is clustering?  
Organizing data based on columns to improve filtering speed.

### ✅ 5. How to reduce BigQuery cost?  
Partition, cluster, avoid SELECT *, filter early.

### ✅ 6. What is federated query?  
Query external sources (GCS, Bigtable) without loading data.

---

# ✅ 13. Summary (Easy English)

- BigQuery = Google’s fastest database for analytics  
- Serverless → you don’t manage servers  
- Ideal for TB-to-PB‑scale data  
- Very cheap if you use **partitioning + clustering**  
- SQL-based → very easy to use  

---
