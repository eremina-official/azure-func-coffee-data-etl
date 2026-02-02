import azure.functions as func
import logging
import json
from src.db.db_connection import get_cursor
from src.db.insert_product_helpers import (
    insert_product,
    insert_parameter,
    insert_parameter_value,
    map_product_parameter,
)
from src.models.product import Product
from src.utils.constants import VALUES_LABELS, VALUES_IDS


# Coffee categories to process
COFFEE_CATEGORY_IDS = ("74035", "74033", "261120")


def run_products_pipeline(raw_products, cursor):
    for raw in raw_products:
        if raw.get("category", {}).get("id") not in COFFEE_CATEGORY_IDS:
            continue

        product = Product(**raw).to_db_dict()

        # Insert product
        insert_product(product, cursor)

        # Insert parameters and values
        for param in product.get("parameters", []):
            if "valuesIds" not in param:
                continue

            insert_parameter(param, cursor)

            values_labels = param.get(VALUES_LABELS, []) or []
            values_values = param.get("values", values_labels) or []

            if not values_values:
                values_values = [None] * len(values_labels)

            values_ids = (
                param.get(
                    VALUES_IDS,
                    [f'{param["id"]}_{i}' for i in range(len(values_labels))],
                )
                or []
            )

            for vid, label, val in zip(values_ids, values_labels, values_values):
                insert_parameter_value(
                    param_id=param["id"],
                    value_id=vid,
                    label=label,
                    value=val,
                    cursor=cursor,
                )
                map_product_parameter(
                    product_id=product["id"], value_id=vid, cursor=cursor
                )

        logging.info(f"Inserted product: {product.get('id')}")


# --- Azure Function Entry Point ---
app = func.FunctionApp()

# @app.blob_trigger(
#     arg_name="myblob",
#     source="EventGrid",
#     path="jsonfiles",
#     connection=os.environ.get("AzureWebJobsStorage")
# )


@app.blob_trigger(arg_name="blob", path="jsonfiles", connection="AzureWebJobsStorage")
def process_product_blob(blob: func.InputStream):
    logging.info(f"Processing blob: {blob.name}")

    # Idempotency: check if blob already processed
    cursor, conn = get_cursor()
    try:
        # Load blob content
        content = blob.read().decode("utf-8")
        data = json.loads(content)
        raw_products = data.get("products", [])
        cursor.execute("SELECT DATABASE(), CURRENT_USER()")
        db, user = cursor.fetchone()
        logging.info(f"Connected to DB={db}, USER={user}")
        # Run your pipeline
        run_products_pipeline(raw_products, cursor)

        # Commit transaction
        conn.commit()

        logging.info(f"Finished processing blob: {blob.name}")

    except Exception as e:
        logging.error(f"Error during processing: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()
