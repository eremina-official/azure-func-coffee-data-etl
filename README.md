## Azure Functions App for Coffee Data ETL project

### Overview

This project is an **Azure Functions** application which is part of an **end-to-end data ETL pipeline** for coffee data analysis. The function is triggered by new JSON blobs uploaded to a configured **Azure Blob Storage** container (Blob trigger). The app validates and normalizes data with Python + Pydantic and saves to the golden dataset in MySQL.

---

### Project Architecture
![Screenshot of Project ETL Pipeline](/src/assets/azure-coffee-etl.png)

### Azure Blob Storage

- All API responses stored as raw JSON coffee catalog files; each new blob fires the trigger that starts the ETL.
- Raw files are **immutable** (corrections are applied downstream only).
- Blob names are deterministic and include **timestamps**.

### Azure Function App (Transformation & Load)

A **blob-triggered** Azure Function processes new files.

***Why Azure Functions:***

- Event-driven architecture
- No need for long-running compute clusters (data do not arrive continuously)
- **Cost-efficient** for sporadic ingestion (pay-per-use)

Trade-off: Functions are not ideal for very large files or heavy parallelism, but our use case involves small JSON files and moderate throughput, making it a good fit.

### Azure Database for MySQL Flexible Server

Structured, validated data is stored in MySQL using a normalized schema (**snowflake schema**)

***Why relational storage:***

- Clear entity relationships.
- Dictionary tables are **populated once and reused**.
- Efficient **filtering** via indexing makes it a better fit for analytical SQL exploration.

### Power BI

Consumes the curated tables (views) and presents dashboards.

---

### Data Modeling Decisions

The source API provides dynamic product attributes (brand, origin, roast type, etc.). Instead of flattening everything into a wide table, a **dictionary-driven relational model** was chosen.

Core entities:
- `products`
- `categories`
- `parameters`
- `parameter_values`
- `product_parameter_values` (many-to-many bridge)

**Why This Design?**

- **Prevents duplication** of attribute metadata
- Allows **multi-valued attributes** per product
- Enables flexible **parameter-based filtering** required for data exploration

**Validation & Data Quality**

Validation is enforced at transformation time using typed models (`Pydantic`).

Rules Applied:
- Required identifiers must be present
- Non-coffee products filtered out
- Measurement units standardized
- Inconsistent parameters excluded

---

### Failure Handling & Observability

- Structured logging for each transformation stage
- Explicit error logging for validation failures
- Avoid partial writes

If a failure occurs mid-processing, the file can be safely reprocessed due to idempotent design.

---

### Pricing & Cost of Azure Services

- **Azure Functions**: Pay-per-use model; costs depend on execution time and memory. For small, infrequent files costs are minimal.
- **Azure Blob Storage**: Costs based on storage and transactions. Raw JSON files are small, so storage costs are low.
- **Azure Database for MySQL**: Costs depend on compute and storage. ***In the currect project cost of the MySQL server was the highest from all pipeline components. After initial setup, costs were optimized by scaling down during low usage periods.***

---

### Project Structure
```
├── function_app.py
├── host.json
├── local.settings.json
├── requirements.txt
└── src/
    ├── db/
    │   ├── db_connection.py
    │   └── insert_product_helpers.py
    ├── models/
    │   └── product.py
    └── utils/
        └── constants.py
```

---

### Requirements
- Python 3.x
- Azure Functions Core Tools
- Required Python packages listed in `requirements.txt`

### Setup
1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd azure-func-coffee-data-etl
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure your local settings in `local.settings.json`.

4. Start the Azure Functions host locally:
   ```bash
   func start
   ```

### Deploy to Azure
- Prerequisites: Azure CLI and Azure Functions Core Tools installed, and an Azure subscription.
- Quick deploy using the Core Tools:
  ```bash
  az login
  func azure functionapp publish <FUNCTION_APP_NAME>
  ```

### License
MIT License.
