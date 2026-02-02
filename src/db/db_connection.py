import os
import mysql.connector
from mysql.connector.cursor import MySQLCursor


def get_connection():
    return mysql.connector.connect(
        host=os.environ.get("MYSQL_HOST"),
        database=os.environ.get("MYSQL_DATABASE"),
        user=os.environ.get("MYSQL_USER"),
        password=os.environ.get("MYSQL_PASSWORD"),
    )


def get_cursor() -> MySQLCursor:
    """Return a cursor from a connection (caller must close connection)."""
    conn = get_connection()
    return conn.cursor(), conn
