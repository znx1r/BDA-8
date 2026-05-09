"""
DAG de usuarios — Parte B
Pipeline independiente que crea la base de datos SQLite de autenticación
e inserta los usuarios del sistema con contraseñas cifradas.

Usuarios insertados:
    admin   · rol: admin
    profesor · rol: profesor
    alumno  · rol: alumno
"""

from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import sqlite3
from datetime import datetime, timedelta

from werkzeug.security import generate_password_hash
from airflow import DAG
from airflow.operators.python import PythonOperator

from models.db.querys import (
    CREATE_SQLITE_USUARIOS, CREATE_SQLITE_INDEX_USERNAME, CREATE_SQLITE_INDEX_EMAIL,
    SELECT_USUARIO_EXISTS, INSERT_USUARIO,
)
from models.dag.utils import USUARIOS
from config import SQLITE_PATH


# Tarea 1: comprobar conexión con SQLite

def check_sqlite():
    conn = sqlite3.connect(SQLITE_PATH)
    cur  = conn.cursor()
    cur.execute("SELECT sqlite_version();")
    version = cur.fetchone()[0]
    conn.close()
    print(f"[OK] SQLite {version} — base de datos en: {SQLITE_PATH}")


# Tarea 2: crear tabla de usuarios e índices en SQLite

def create_users_table():
    conn = sqlite3.connect(SQLITE_PATH)
    cur  = conn.cursor()
    try:
        cur.execute(CREATE_SQLITE_USUARIOS)
        cur.execute(CREATE_SQLITE_INDEX_USERNAME)
        cur.execute(CREATE_SQLITE_INDEX_EMAIL)
        conn.commit()
        print("[OK] Tabla 'usuarios' creada / verificada.")
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


# Tarea 3: insertar usuarios con contraseñas cifradas

def insert_users():
    conn = sqlite3.connect(SQLITE_PATH)
    cur  = conn.cursor()

    try:
        inserted = 0
        skipped  = 0

        for u in USUARIOS:
            cur.execute(SELECT_USUARIO_EXISTS, (u["username"],))
            if cur.fetchone():
                print(f"[SKIP] Usuario '{u['username']}' ya existe.")
                skipped += 1
                continue

            password_hash = generate_password_hash(u["password"], method="pbkdf2:sha256")
            cur.execute(
                INSERT_USUARIO,
                (
                    u["username"],
                    u["email"],
                    password_hash,
                    u["nombre"],
                    u["rol"],
                    u["is_active"],
                    datetime.utcnow().isoformat(),
                ),
            )
            print(f"[OK] Usuario '{u['username']}' insertado con rol '{u['rol']}'.")
            inserted += 1

        conn.commit()
        print(f"[OK] Resultado: {inserted} insertados, {skipped} omitidos.")

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


# Definición del DAG y dependencias entre tareas

default_args = {
    "owner":            "academico",
    "retries":          1,
    "retry_delay":      timedelta(minutes=2),
    "email_on_failure": False,
}

with DAG(
    dag_id="dag_usuarios_sqlite",
    description="Crea la base de datos SQLite de autenticación e inserta usuarios con contraseñas cifradas.",
    schedule_interval=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    default_args=default_args,
    tags=["autenticacion", "sqlite", "usuarios"],
) as dag:

    t1 = PythonOperator(
        task_id="comprobar_sqlite",
        python_callable=check_sqlite,
    )

    t2 = PythonOperator(
        task_id="crear_tabla_usuarios",
        python_callable=create_users_table,
    )

    t3 = PythonOperator(
        task_id="insertar_usuarios",
        python_callable=insert_users,
    )

    t1 >> t2 >> t3
