# db/insert_parameter.py

def insert_category(category, cursor):
    """Insert category and its parent recursively."""
    parent_id = category.get("parent_id", None)
    cursor.execute(
        "INSERT IGNORE INTO categories (id, name, parent_id) VALUES (%s, %s, %s)",
        (category["id"], category["name"], parent_id),
    )


def insert_parameter(param: dict, cursor):
    """
    Insert a parameter into 'parameters' table.
    Expects a dict with keys: id, name, unit, identifies_product
    Idempotent: skips existing records
    """
    cursor.execute(
        "INSERT IGNORE INTO parameters (id, name, unit, identifies_product) VALUES (%s, %s, %s, %s)",
        (
            param["id"],
            param["name"],
            param.get("unit"),
            param.get("options", {}).get("identifiesProduct", False),
        ),
    )


def insert_parameter_value(param_id, value_id, label, value, cursor):
    """Insert parameter value only if it does not exist."""
    cursor.execute(
        "INSERT IGNORE INTO parameter_values (id, parameter_id, label, value) VALUES (%s, %s, %s, %s)",
        (value_id, param_id, label, value),
    )


def map_product_parameter(product_id, value_id, cursor):
    """Map product to parameter value."""
    cursor.execute(
        "INSERT IGNORE INTO product_parameter_values (product_id, value_id) VALUES (%s, %s)",
        (product_id, value_id),
    )


def insert_product(product_dict: dict, cursor):
    """
    Insert a product into 'products' table.

    Expects a dictionary with keys:
    id, name, category_id, publication_status, description, images, ean

    - description: dict → stored as JSON
    - images: list → stored as JSON
    - Idempotent: INSERT IGNORE avoids duplicates
    """
    cursor.execute(
        """
        INSERT IGNORE INTO products
        (id, name, category_id, publication_status, description, images, ean)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (
            product_dict["id"],
            product_dict["name"],
            product_dict["category_id"],
            product_dict.get("publication_status"),
            product_dict.get("description", {}),
            product_dict.get("images", []),
            product_dict.get("ean"),
        ),
    )
