import os
import mysql.connector
from mysql.connector.cursor import MySQLCursor


def get_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        database=os.getenv("MYSQL_DATABASE"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
    )


def get_cursor() -> MySQLCursor:
    """Return a cursor from a connection (caller must close connection)."""
    conn = get_connection()
    return conn.cursor(), conn
