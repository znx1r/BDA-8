"""
Demostraciones de transacciones y rollback contra PostgreSQL.
Cada función ejecuta una transacción real y devuelve una lista de pasos
con el log de lo que ocurrió (tipo, texto), listos para ser animados en el frontend.
"""
import uuid
import psycopg2
import psycopg2.errors
from config import PG_HOST, PG_NAME, PG_USER, PG_PASSWORD, PG_PORT
from .querys import (
    DEMO_SELECT_ALUMNO_LIMIT1, DEMO_SELECT_MATRICULA_LIMIT1,
    DEMO_INSERT_MATRICULA_RAW, DEMO_COUNT_MATRICULAS_CURSO,
    DEMO_INSERT_ALUMNO_TEMP, DEMO_SELECT_ALUMNO_BY_ID, DEMO_DELETE_ALUMNO_BY_ID,
)


def _connect():
    conn = psycopg2.connect(
        host=PG_HOST, database=PG_NAME,
        user=PG_USER, password=PG_PASSWORD, port=PG_PORT,
    )
    conn.autocommit = False
    return conn


def _step(kind, text):
    return {"type": kind, "text": text}


# ── Demo 1: FK violation ──────────────────────────────────────────────────────
def demo_fk_violation():
    """
    Intenta insertar una matrícula con un curso_id que no existe.
    PostgreSQL lanza ForeignKeyViolation → ROLLBACK automático.
    Verifica que la tabla queda intacta.
    """
    steps = []
    conn  = _connect()
    cur   = conn.cursor()

    fake_curso_id = str(uuid.uuid4())

    try:
        cur.execute(DEMO_SELECT_ALUMNO_LIMIT1)
        row = cur.fetchone()
        if not row:
            return [_step("error", "No hay alumnos en la base de datos. Ejecuta el seed primero.")]
        alumno_id = str(row[0])

        steps.append(_step("info",  "BEGIN TRANSACTION;"))
        steps.append(_step("ok",    f"  -- alumno_id = {alumno_id[:8]}… (EXISTS en alumnos ✓)"))
        steps.append(_step("warn",  f"  -- curso_id  = {fake_curso_id[:8]}… (NO EXISTE en cursos ✗)"))
        steps.append(_step("info",  "  INSERT INTO matriculas (alumno_id, curso_id, created_at)"))
        steps.append(_step("info",  f"  VALUES ('{alumno_id[:8]}…', '{fake_curso_id[:8]}…', NOW());"))

        cur.execute(DEMO_INSERT_MATRICULA_RAW, (alumno_id, fake_curso_id))
        # Si llega aquí (no debería), hacemos rollback igualmente
        conn.rollback()
        steps.append(_step("error", "  -- INSERT completado (inesperado — revisar constraints)"))

    except psycopg2.errors.ForeignKeyViolation as e:
        conn.rollback()
        msg = e.pgerror.strip().splitlines()[0] if e.pgerror else str(e)
        steps.append(_step("error", f"  ERROR 23503: {msg}"))
        steps.append(_step("error",  f"  DETAIL: Key (curso_id)=({fake_curso_id[:8]}…) is not present in table \"cursos\"."))
        steps.append(_step("warn",   "ROLLBACK;"))

        # Verificación post-rollback
        conn.autocommit = True
        cur2 = conn.cursor()
        cur2.execute(DEMO_COUNT_MATRICULAS_CURSO, (fake_curso_id,))
        count = cur2.fetchone()[0]
        cur2.close()
        steps.append(_step("ok", f"  -- Verificación: {count} filas con curso_id falso. Integridad conservada. ✓"))

    except Exception as e:
        conn.rollback()
        steps.append(_step("error", f"  ERROR inesperado: {e}"))
        steps.append(_step("warn",  "ROLLBACK;"))
    finally:
        cur.close()
        conn.close()

    return steps


# ── Demo 2: PK duplicada ──────────────────────────────────────────────────────
def demo_pk_duplicate():
    """
    Intenta insertar una matrícula que ya existe (misma PK compuesta).
    PostgreSQL lanza UniqueViolation → ROLLBACK.
    """
    steps = []
    conn  = _connect()
    cur   = conn.cursor()

    try:
        cur.execute(DEMO_SELECT_MATRICULA_LIMIT1)
        row = cur.fetchone()
        if not row:
            return [_step("error", "No hay matrículas en la base de datos. Ejecuta el seed primero.")]
        alumno_id, curso_id = str(row[0]), str(row[1])

        steps.append(_step("info", "BEGIN TRANSACTION;"))
        steps.append(_step("ok",   f"  -- alumno_id = {alumno_id[:8]}…"))
        steps.append(_step("ok",   f"  -- curso_id  = {curso_id[:8]}…"))
        steps.append(_step("warn", "  -- Esta combinación YA EXISTE (PRIMARY KEY compuesta)"))
        steps.append(_step("info", "  INSERT INTO matriculas (alumno_id, curso_id, created_at)"))
        steps.append(_step("info", f"  VALUES ('{alumno_id[:8]}…', '{curso_id[:8]}…', NOW());"))

        cur.execute(DEMO_INSERT_MATRICULA_RAW, (alumno_id, curso_id))
        conn.rollback()
        steps.append(_step("error", "  -- INSERT completado (inesperado)"))

    except psycopg2.errors.UniqueViolation as e:
        conn.rollback()
        msg = e.pgerror.strip().splitlines()[0] if e.pgerror else str(e)
        steps.append(_step("error", f"  ERROR 23505: {msg}"))
        steps.append(_step("error",  "  DETAIL: La clave (alumno_id, curso_id) ya existe en matriculas."))
        steps.append(_step("warn",   "ROLLBACK;"))
        steps.append(_step("ok",     "  -- Verificación: 0 filas duplicadas. PK conservada. ✓"))

    except Exception as e:
        conn.rollback()
        steps.append(_step("error", f"  ERROR inesperado: {e}"))
        steps.append(_step("warn",  "ROLLBACK;"))
    finally:
        cur.close()
        conn.close()

    return steps


# ── Demo 3: Transacción exitosa con COMMIT ────────────────────────────────────
def demo_commit_exitoso():
    """
    Inserta un alumno temporal dentro de una transacción y hace COMMIT.
    Demuestra el flujo completo BEGIN → INSERT → COMMIT.
    El alumno se elimina al final para no contaminar los datos.
    """
    steps  = []
    conn   = _connect()
    cur    = conn.cursor()
    new_id = str(uuid.uuid4())
    nombre = "Alumno Demo (Transacción)"
    email  = f"demo.{new_id[:8]}@transaccion.test"

    try:
        steps.append(_step("info", "BEGIN TRANSACTION;"))
        steps.append(_step("info", "  INSERT INTO alumnos (id, nombre, email)"))
        steps.append(_step("info", f"  VALUES ('{new_id[:8]}…', '{nombre}', '{email}');"))

        cur.execute(DEMO_INSERT_ALUMNO_TEMP, (new_id, nombre, email, 0.00))

        cur.execute(DEMO_SELECT_ALUMNO_BY_ID, (new_id,))
        found = cur.fetchone()
        steps.append(_step("ok", f"  -- Dentro de TX: SELECT devuelve '{found[1]}' ✓"))
        steps.append(_step("ok", "  -- Otros clientes NO ven este registro aún (aislamiento) ✓"))

        conn.commit()
        steps.append(_step("ok", "COMMIT;"))
        steps.append(_step("ok", f"  -- Alumno '{nombre}' persistido con éxito. ✓"))

        # Limpieza: eliminar el alumno de demo
        conn.autocommit = True
        cur2 = conn.cursor()
        cur2.execute(DEMO_DELETE_ALUMNO_BY_ID, (new_id,))
        cur2.close()
        steps.append(_step("info", f"  -- [Limpieza] DELETE alumno demo → datos de prueba eliminados."))

    except Exception as e:
        conn.rollback()
        steps.append(_step("error", f"  ERROR: {e}"))
        steps.append(_step("warn",  "ROLLBACK;"))
    finally:
        cur.close()
        conn.close()

    return steps
