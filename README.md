## Azure Functions Coffee Data ETL

### Overview
This project is an **Azure Functions** application designed to extract, transform, and load (ETL) json files with coffee data. It utilizes Azure services for data storage and processing, making it efficient and scalable. The function is triggered by new JSON blobs uploaded to a configured Azure Blob Storage container (Blob trigger).

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
This project is licensed under the MIT License.
