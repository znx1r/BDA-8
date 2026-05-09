from functools import wraps
import sqlite3
import psycopg2
from config import (
    PG_HOST, PG_NAME, PG_PASSWORD, PG_PORT, PG_USER, SQLITE_PATH
)

# Operaciones de lectura
def with_cursor(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        conn = None
        try:
            conn = psycopg2.connect(
                host=PG_HOST,
                database=PG_NAME,
                user=PG_USER,
                password=PG_PASSWORD,
                port=PG_PORT,
            )
            conn.autocommit = True
            
            cursor = conn.cursor()
            result = f(args[0], cursor, *args[1:], **kwargs)
            return(result)
        except (Exception, psycopg2.DatabaseError) as e:
            print("Error:", e)
            if conn: conn.rollback()
        finally:
            if conn is not None: conn.close()
    return wrapper

def with_transactions(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        conn = None
        try:
            conn = psycopg2.connect(
                host=PG_HOST,
                database=PG_NAME,
                user=PG_USER,
                password=PG_PASSWORD,
                port=PG_PORT,
            )
            cursor = conn.cursor()
            result = f(args[0], cursor, *args[1:], **kwargs)
            conn.commit()
            return result
        except (Exception, psycopg2.DatabaseError) as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn is not None:
                cursor.close()
                conn.close()
    return wrapper

def with_connection(f):
    """
    Pasa (conn, cursor) a la función para que ella misma gestione
    BEGIN / COMMIT / ROLLBACK. Útil para transacciones complejas con pasos intermedios.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        conn = None
        try:
            conn = psycopg2.connect(
                host=PG_HOST,
                database=PG_NAME,
                user=PG_USER,
                password=PG_PASSWORD,
                port=PG_PORT,
            )
            conn.autocommit = False
            cursor = conn.cursor()
            return f(args[0], conn, cursor, *args[1:], **kwargs)
        except (Exception, psycopg2.DatabaseError) as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if conn is not None:
                conn.close()
    return wrapper


def with_sqlite(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect(SQLITE_PATH)
        conn.row_factory = sqlite3.Row
        try:
            cursor = conn.cursor()
            result = f(args[0], cursor, *args[1:], **kwargs)
            return result
        except Exception as e:
            print("Error SQLite:", e)
            return None
        finally:
            conn.close()
    return wrapper