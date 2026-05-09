"""
DAG académico — Parte A
Pipeline que comprueba la conexión con PostgreSQL, crea el esquema académico
y carga un dataset mínimo de prueba.

Tablas gestionadas:
    profesores, alumnos, cursos, matriculas

Dataset mínimo:
    10 profesores · 100 alumnos · 20 cursos · 200 matrículas
"""

from __future__ import annotations

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import uuid
import random
from datetime import datetime, timezone, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from models.db.querys import (
    CREATE_PROFESORES, CREATE_ALUMNOS, CREATE_CURSOS, CREATE_MATRICULAS,
    CREATE_INDEX_CURSOS_PROFESOR_ID, CREATE_INDEX_MATRICULAS_CURSO_ID, CREATE_INDEX_ALUMNOS_EMAIL,
)
from models.dag.utils import get_pg_conn, already_seeded, PROFESORES_NOMBRES, CURSOS


# Tarea 1: comprobar conexión con PostgreSQL

def check_connection():
    conn = get_pg_conn()
    cur  = conn.cursor()
    cur.execute("SELECT version();")
    version = cur.fetchone()[0]
    cur.close()
    conn.close()
    print(f"[OK] Conexión establecida: {version}")


# Tarea 2: crear esquema de tablas e índices en PostgreSQL

DDL_INDEXES = [
    CREATE_INDEX_ALUMNOS_EMAIL,
    CREATE_INDEX_CURSOS_PROFESOR_ID,
    CREATE_INDEX_MATRICULAS_CURSO_ID,
]


def create_schema():
    conn = get_pg_conn()
    cur  = conn.cursor()
    try:
        cur.execute(CREATE_PROFESORES)
        cur.execute(CREATE_ALUMNOS)
        cur.execute(CREATE_CURSOS)
        cur.execute(CREATE_MATRICULAS)
        for idx in DDL_INDEXES:
            cur.execute(idx)
        conn.commit()
        print("[OK] Esquema académico creado / verificado.")
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()


# Tarea 3: insertar dataset mínimo de prueba

def insert_data():
    conn = get_pg_conn()
    cur  = conn.cursor()

    try:
        # Tarea 3a: insertar 10 profesores
        if already_seeded(cur, "profesores", 10):
            print("[SKIP] profesores — ya contiene datos suficientes.")
            cur.execute("SELECT id FROM profesores LIMIT 10;")
            profesor_ids = [str(r[0]) for r in cur.fetchall()]
        else:
            profesor_ids = []
            for nombre in PROFESORES_NOMBRES:
                pid = str(uuid.uuid4())
                cur.execute(
                    "INSERT INTO profesores (id, nombre) VALUES (%s, %s) ON CONFLICT DO NOTHING;",
                    (pid, nombre),
                )
                profesor_ids.append(pid)
            print(f"[OK] {len(profesor_ids)} profesores insertados.")

        # Tarea 3b: insertar 100 alumnos
        if already_seeded(cur, "alumnos", 100):
            print("[SKIP] alumnos — ya contiene datos suficientes.")
            cur.execute("SELECT id FROM alumnos LIMIT 100;")
            alumno_ids = [str(r[0]) for r in cur.fetchall()]
        else:
            alumno_ids = []
            for i in range(1, 101):
                aid    = str(uuid.uuid4())
                nombre = f"Alumno DAG {i:03d}"
                email  = f"alumno.dag{i:03d}@academico.es"
                cur.execute(
                    "INSERT INTO alumnos (id, nombre, email) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING;",
                    (aid, nombre, email),
                )
                alumno_ids.append(aid)
            print(f"[OK] {len(alumno_ids)} alumnos insertados.")

        # Tarea 3c: insertar 20 cursos
        if already_seeded(cur, "cursos", 20):
            print("[SKIP] cursos — ya contiene datos suficientes.")
            cur.execute("SELECT id FROM cursos LIMIT 20;")
            curso_ids = [str(r[0]) for r in cur.fetchall()]
        else:
            curso_ids = []
            for i, (nombre, nombre_en) in enumerate(CURSOS):
                cid = str(uuid.uuid4())
                pid = profesor_ids[i % len(profesor_ids)]
                cur.execute(
                    "INSERT INTO cursos (id, nombre, nombre_en, profesor_id) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING;",
                    (cid, nombre, nombre_en, pid),
                )
                curso_ids.append(cid)
            print(f"[OK] {len(curso_ids)} cursos insertados.")

        # Tarea 3d: insertar 200 matrículas
        if already_seeded(cur, "matriculas", 200):
            print("[SKIP] matriculas — ya contiene datos suficientes.")
        else:
            inserted  = 0
            seen      = set()
            attempts  = 0
            base_date = datetime(2024, 1, 1, tzinfo=timezone.utc)

            while inserted < 200 and attempts < 2000:
                attempts += 1
                aid = random.choice(alumno_ids)
                cid = random.choice(curso_ids)
                if (aid, cid) in seen:
                    continue
                seen.add((aid, cid))
                created_at = base_date + timedelta(days=random.randint(0, 500))
                cur.execute(
                    """INSERT INTO matriculas (alumno_id, curso_id, created_at)
                       VALUES (%s, %s, %s) ON CONFLICT DO NOTHING;""",
                    (aid, cid, created_at),
                )
                inserted += 1

            print(f"[OK] {inserted} matrículas insertadas.")

        conn.commit()
        print("[OK] Dataset mínimo cargado correctamente.")

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()


# Definición del DAG y dependencias entre tareas

default_args = {
    "owner":            "academico",
    "retries":          1,
    "retry_delay":      timedelta(minutes=2),
    "email_on_failure": False,
}

with DAG(
    dag_id="dag_academico_postgresql",
    description="Comprueba conexión, crea esquema académico e inserta dataset mínimo.",
    schedule_interval=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    default_args=default_args,
    tags=["academico", "bda", "postgresql"],
) as dag:

    t1 = PythonOperator(
        task_id="comprobar_conexion",
        python_callable=check_connection,
    )

    t2 = PythonOperator(
        task_id="crear_esquema",
        python_callable=create_schema,
    )

    t3 = PythonOperator(
        task_id="insertar_datos",
        python_callable=insert_data,
    )

    t1 >> t2 >> t3
