from .decorators import with_cursor, with_transactions, with_connection
from .querys import (
    SELECT_VERSION, SELECT_ALL_PROFESORES, SELECT_ALL_ALUMNOS,
    SELECT_ALL_CURSOS, SELECT_ALL_MATRICULAS,
    SELECT_ALUMNOS_WITH_COUNT, SELECT_PROFESORES_WITH_COUNT,
    SELECT_CURSOS_WITH_COUNT, SELECT_MATRICULAS_FULL,
    SELECT_PROFESOR_BY_ID, SELECT_CURSOS_BY_PROFESOR,
    SELECT_ALUMNO_BY_ID, SELECT_CURSOS_BY_ALUMNO,
    SELECT_CURSO_BY_ID, SELECT_ALUMNOS_BY_CURSO,
    CHECK_MATRICULA_EXISTS,
    DELETE_PROFESOR, DELETE_ALUMNO, DELETE_CURSO, DELETE_MATRICULA,
    COUNT_PROFESORES, COUNT_ALUMNOS, COUNT_CURSOS, COUNT_MATRICULAS,
    CREATE_ALUMNOS, CREATE_CURSOS, CREATE_MATRICULAS, CREATE_PROFESORES,
    CREATE_INDEX_CURSOS_PROFESOR_ID, CREATE_INDEX_MATRICULAS_CURSO_ID, CREATE_INDEX_ALUMNOS_EMAIL,
    INSERT_ALUMNOS, INSERT_PROFESORES, INSERT_CURSOS, INSERT_MATRICULAS,
    CREATE_AUDITORIA, CREATE_INDEX_AUDITORIA_ENTIDAD,
    INSERT_AUDITORIA, SELECT_ALL_AUDITORIA, COUNT_AUDITORIA,
    DELETE_AUDITORIA, DELETE_ALL_AUDITORIA,
    ALTER_ALUMNOS_SALDO, ALTER_CURSOS_PRECIO, ALTER_CURSOS_MAX_ALUMNOS, ALTER_CURSOS_NOMBRE_EN,
    CREATE_EXTENSION_UNACCENT, CREATE_EXTENSION_CITEXT, CREATE_EXTENSION_FUZZYSTRMATCH,
    CREATE_EXTENSION_BTREE_GIN, CREATE_EXTENSION_PG_TRGM,
    CREATE_INDEX_CURSOS_NOMBRE_TRGM, CREATE_INDEX_CURSOS_NOMBRE_EN_TRGM,
    CREATE_INDEX_ALUMNOS_NOMBRE_TRGM, CREATE_INDEX_PROFESORES_NOMBRE_TRGM,
    SELECT_ALUMNO_FOR_ENROLL, SELECT_CURSO_FOR_ENROLL,
    UPDATE_ALUMNO_SALDO, UPDATE_CURSO_SETTINGS, UPDATE_ALUMNO_RECHARGE, UPDATE_CURSO_NOMBRE_EN,
    CREATE_VISTA_MATRICULAS, SELECT_VISTA_MATRICULAS, COUNT_VISTA_MATRICULAS,
    CREATE_INDEX_ALUMNOS_NOMBRE, CREATE_INDEX_ALUMNOS_SALDO,
    CREATE_INDEX_CURSOS_NOMBRE, CREATE_INDEX_CURSOS_PRECIO, CREATE_INDEX_CURSOS_MAX_ALUMNOS,
    CREATE_INDEX_PROFESORES_NOMBRE,
    CREATE_INDEX_MATRICULAS_DATE,
    CREATE_INDEX_AUDITORIA_DATE, CREATE_INDEX_AUDITORIA_ACCION, CREATE_INDEX_AUDITORIA_USUARIO,
    SELECT_ALUMNOS_FILTER_BASE, SELECT_ALUMNOS_FILTER_TAIL,
    SELECT_CURSOS_FILTER_BASE, SELECT_CURSOS_FILTER_GROUP, SELECT_CURSOS_FILTER_ORDER,
    SELECT_PROFESORES_FILTER_BASE, SELECT_PROFESORES_FILTER_GROUP, SELECT_PROFESORES_FILTER_ORDER,
    SELECT_MATRICULAS_FILTER_BASE, SELECT_MATRICULAS_FILTER_TAIL,
    SELECT_VISTA_FILTER_BASE, SELECT_VISTA_FILTER_TAIL,
    SELECT_AUDITORIA_FILTER_BASE, SELECT_AUDITORIA_FILTER_TAIL,
    SELECT_ANALITICA_FILTER, SELECT_ANALITICA_ROLLUP,
    SELECT_ANALITICA_GROUPING_SETS, SELECT_ANALITICA_ROW_NUMBER,
)
from .filters import FilterBuilder
from ..entities import Alumnos, Profesores, Cursos, Matriculas
from psycopg2 import Error
# Funciones auxiliares
def validate_email(email: str) -> bool:
    import re
    REGEX_PATTERN = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}" 
    if re.match(REGEX_PATTERN, email):
        return True   
    return False

# Operaciones principales de PostgreSQL
class PostgreSQL():
    # Obtener la version de PostgreSQL
    @with_cursor
    def obtain_database_version(self, cursor):
        cursor.execute(SELECT_VERSION)
        return cursor.fetchone()

    # Extensiones Tema 12 — requieren autocommit, no pueden ir dentro de una transacción
    @with_cursor
    def create_extensions(self, cursor):
        cursor.execute(CREATE_EXTENSION_UNACCENT)
        cursor.execute(CREATE_EXTENSION_CITEXT)
        cursor.execute(CREATE_EXTENSION_FUZZYSTRMATCH)
        cursor.execute(CREATE_EXTENSION_BTREE_GIN)
        cursor.execute(CREATE_EXTENSION_PG_TRGM)

    # Creacion de todas las tablas de Postgresql
    @with_transactions
    def create_tables(self, cursor):
        cursor.execute(CREATE_ALUMNOS)
        cursor.execute(CREATE_PROFESORES)
        cursor.execute(CREATE_CURSOS)
        cursor.execute(CREATE_MATRICULAS)
        cursor.execute(CREATE_INDEX_CURSOS_PROFESOR_ID)
        cursor.execute(CREATE_INDEX_MATRICULAS_CURSO_ID)
        cursor.execute(CREATE_INDEX_ALUMNOS_EMAIL)
        cursor.execute(CREATE_AUDITORIA)
        cursor.execute(CREATE_INDEX_AUDITORIA_ENTIDAD)
        # Migraciones: añadir columnas nuevas si no existen
        cursor.execute(ALTER_ALUMNOS_SALDO)
        cursor.execute(ALTER_CURSOS_PRECIO)
        cursor.execute(ALTER_CURSOS_MAX_ALUMNOS)
        cursor.execute(ALTER_CURSOS_NOMBRE_EN)
        # Vista: alumno / profesor / asignatura
        cursor.execute(CREATE_VISTA_MATRICULAS)
        # Índices B-tree para filtros de rango
        cursor.execute(CREATE_INDEX_ALUMNOS_NOMBRE)
        cursor.execute(CREATE_INDEX_ALUMNOS_SALDO)
        cursor.execute(CREATE_INDEX_CURSOS_NOMBRE)
        cursor.execute(CREATE_INDEX_CURSOS_PRECIO)
        cursor.execute(CREATE_INDEX_CURSOS_MAX_ALUMNOS)
        cursor.execute(CREATE_INDEX_PROFESORES_NOMBRE)
        cursor.execute(CREATE_INDEX_MATRICULAS_DATE)
        cursor.execute(CREATE_INDEX_AUDITORIA_DATE)
        cursor.execute(CREATE_INDEX_AUDITORIA_ACCION)
        cursor.execute(CREATE_INDEX_AUDITORIA_USUARIO)
        # Índices GIN para búsqueda por trigrama (pg_trgm)
        cursor.execute(CREATE_INDEX_CURSOS_NOMBRE_TRGM)
        cursor.execute(CREATE_INDEX_CURSOS_NOMBRE_EN_TRGM)
        cursor.execute(CREATE_INDEX_ALUMNOS_NOMBRE_TRGM)
        cursor.execute(CREATE_INDEX_PROFESORES_NOMBRE_TRGM)
        # Rellenar nombre_en en cursos existentes que aún no lo tienen
        from models.dag.utils import CURSOS
        for nombre_es, nombre_en in CURSOS:
            cursor.execute(UPDATE_CURSO_NOMBRE_EN, (nombre_en, nombre_es))

# Operaciones del profesor
class OperacionesProfesor():
    # Operaciones de lectura   
    @with_cursor
    def get_count(self, cursor):
        cursor.execute(COUNT_PROFESORES)
        result = cursor.fetchone()
        return result[0] if result else 0
    
    @with_cursor
    def get_all_teachers(self, cursor):
        try:
            cursor.execute(SELECT_ALL_PROFESORES)
            return cursor.fetchall()
        except (Exception, Error) as e:
            print("Error al obtener los profesores:", e)
            return []

    @with_cursor
    def get_all_teachers_with_count(self, cursor):
        try:
            cursor.execute(SELECT_PROFESORES_WITH_COUNT)
            return cursor.fetchall()
        except (Exception, Error) as e:
            print("Error al obtener los profesores:", e)
            return []

    @with_cursor
    def get_by_id(self, cursor, profesor_id: str):
        try:
            cursor.execute(SELECT_PROFESOR_BY_ID, (profesor_id,))
            return cursor.fetchone()
        except (Exception, Error) as e:
            print("Error al obtener el profesor:", e)
            return None

    @with_cursor
    def get_cursos_by_profesor(self, cursor, profesor_id: str):
        try:
            cursor.execute(SELECT_CURSOS_BY_PROFESOR, (profesor_id,))
            return cursor.fetchall()
        except (Exception, Error) as e:
            print("Error al obtener los cursos del profesor:", e)
            return []

    
    @with_cursor
    def get_filtered(self, cursor, q=None, cursos_min=None, cursos_max=None,
                     limit=20, offset=0):
        f_where = FilterBuilder()
        f_where.ilike("p.nombre", q)
        where, w_params = f_where.where()
        f_hav = FilterBuilder()
        f_hav.gte("COUNT(DISTINCT c.id)", cursos_min)
        f_hav.lte("COUNT(DISTINCT c.id)", cursos_max)
        having, h_params = f_hav.having()
        sql = (SELECT_PROFESORES_FILTER_BASE + where
               + SELECT_PROFESORES_FILTER_GROUP + having
               + SELECT_PROFESORES_FILTER_ORDER + " LIMIT %s OFFSET %s")
        cursor.execute(sql, w_params + h_params + [limit, offset])
        return cursor.fetchall()

    @with_cursor
    def count_filtered(self, cursor, q=None, cursos_min=None, cursos_max=None):
        f_where = FilterBuilder()
        f_where.ilike("p.nombre", q)
        where, w_params = f_where.where()
        f_hav = FilterBuilder()
        f_hav.gte("COUNT(DISTINCT c.id)", cursos_min)
        f_hav.lte("COUNT(DISTINCT c.id)", cursos_max)
        having, h_params = f_hav.having()
        inner = (SELECT_PROFESORES_FILTER_BASE + where
                 + SELECT_PROFESORES_FILTER_GROUP + having)
        cursor.execute(f"SELECT COUNT(*) FROM ({inner}) sub", w_params + h_params)
        row = cursor.fetchone()
        return row[0] if row else 0

    # Operaciones de escritura
    @with_transactions
    def insert_one_teacher(self, cursor, profesor:Profesores):
        params = (profesor.id, profesor.nombre)
        cursor.execute(INSERT_PROFESORES, params)
        print(f"Se ha ingresado el profesor: {profesor} dentro de la base de datos")

    @with_transactions
    def delete_by_id(self, cursor, profesor_id: str):
        cursor.execute(DELETE_PROFESOR, (profesor_id,))

# Operaciones del Alumno
class OperacionesAlumno():   
    # Operaciones de lectura   
    @with_cursor
    def get_count(self, cursor):
        cursor.execute(COUNT_ALUMNOS)
        result = cursor.fetchone()
        return result[0] if result else 0
    
    @with_cursor
    def get_all_students(self, cursor):
        try:
            cursor.execute(SELECT_ALL_ALUMNOS)
            return cursor.fetchall()
        except (Exception, Error) as e:
            print("Error al obtener los estudiantes:", e)
            return []

    @with_cursor
    def get_all_students_with_count(self, cursor):
        try:
            cursor.execute(SELECT_ALUMNOS_WITH_COUNT)
            return cursor.fetchall()
        except (Exception, Error) as e:
            print("Error al obtener los estudiantes:", e)
            return []

    @with_cursor
    def get_by_id(self, cursor, alumno_id: str):
        try:
            cursor.execute(SELECT_ALUMNO_BY_ID, (alumno_id,))
            return cursor.fetchone()
        except (Exception, Error) as e:
            print("Error al obtener el alumno:", e)
            return None

    @with_cursor
    def get_cursos_by_alumno(self, cursor, alumno_id: str):
        try:
            cursor.execute(SELECT_CURSOS_BY_ALUMNO, (alumno_id,))
            return cursor.fetchall()
        except (Exception, Error) as e:
            print("Error al obtener los cursos del alumno:", e)
            return []


    @with_cursor
    def get_filtered(self, cursor, q=None, saldo_min=None, saldo_max=None,
                     limit=20, offset=0):
        f = FilterBuilder()
        f.ilike_any(["a.nombre", "a.email"], q)
        f.gte("a.saldo", saldo_min)
        f.lte("a.saldo", saldo_max)
        where, params = f.where()
        sql = SELECT_ALUMNOS_FILTER_BASE + where + SELECT_ALUMNOS_FILTER_TAIL + " LIMIT %s OFFSET %s"
        cursor.execute(sql, params + [limit, offset])
        return cursor.fetchall()

    @with_cursor
    def count_filtered(self, cursor, q=None, saldo_min=None, saldo_max=None):
        f = FilterBuilder()
        f.ilike_any(["a.nombre", "a.email"], q)
        f.gte("a.saldo", saldo_min)
        f.lte("a.saldo", saldo_max)
        where, params = f.where()
        sql = "SELECT COUNT(*) FROM (SELECT a.id FROM alumnos a LEFT JOIN matriculas m ON a.id = m.alumno_id" + where + " GROUP BY a.id) sub"
        cursor.execute(sql, params)
        row = cursor.fetchone()
        return row[0] if row else 0

    # Operaciones de escritura
    @with_transactions
    def insert_one_student(self, cursor, alumno:Alumnos):
        if not alumno.email or not validate_email(alumno.email):
            raise Exception("Hay un error procesando el correo electrónico.")
        params = (alumno.id, alumno.nombre, alumno.email, alumno.saldo)
        cursor.execute(INSERT_ALUMNOS, params)
        print(f"Se ha ingresado el alumno: {alumno} dentro de la base de datos")

    @with_transactions
    def recharge_saldo(self, cursor, alumno_id: str, cantidad: float):
        cursor.execute(UPDATE_ALUMNO_RECHARGE, (cantidad, alumno_id))

    @with_transactions
    def delete_by_id(self, cursor, alumno_id: str):
        cursor.execute(DELETE_ALUMNO, (alumno_id,))

# Operaciones del Curso
class OperacionesCurso():
    @with_cursor
    def get_count(self, cursor):
        cursor.execute(COUNT_CURSOS)
        result = cursor.fetchone()
        return result[0] if result else 0

    @with_cursor
    def get_all_courses(self, cursor):
        try:
            cursor.execute(SELECT_ALL_CURSOS)
            return cursor.fetchall()
        except (Exception, Error) as e:
            print("Error al obtener los cursos:", e)
            return []

    @with_cursor
    def get_all_courses_with_count(self, cursor):
        try:
            cursor.execute(SELECT_CURSOS_WITH_COUNT)
            return cursor.fetchall()
        except (Exception, Error) as e:
            print("Error al obtener los cursos:", e)
            return []

    @with_cursor
    def get_by_id(self, cursor, curso_id: str):
        try:
            cursor.execute(SELECT_CURSO_BY_ID, (curso_id,))
            return cursor.fetchone()
        except (Exception, Error) as e:
            print("Error al obtener el curso:", e)
            return None

    @with_cursor
    def get_alumnos_by_curso(self, cursor, curso_id: str):
        try:
            cursor.execute(SELECT_ALUMNOS_BY_CURSO, (curso_id,))
            return cursor.fetchall()
        except (Exception, Error) as e:
            print("Error al obtener los alumnos del curso:", e)
            return []

    @with_cursor
    def get_filtered(self, cursor, q=None, precio_min=None, precio_max=None,
                     max_min=None, max_max=None, limit=20, offset=0):
        f_where = FilterBuilder()
        f_where.unaccent_ilike_any(["c.nombre", "c.nombre_en"], q)
        f_where.gte("c.precio", precio_min)
        f_where.lte("c.precio", precio_max)
        where, w_params = f_where.where()
        f_hav = FilterBuilder()
        f_hav.gte("(c.max_alumnos - COUNT(m.alumno_id))", max_min)
        f_hav.lte("(c.max_alumnos - COUNT(m.alumno_id))", max_max)
        having, h_params = f_hav.having()
        sql = (SELECT_CURSOS_FILTER_BASE + where
               + SELECT_CURSOS_FILTER_GROUP + having
               + SELECT_CURSOS_FILTER_ORDER + " LIMIT %s OFFSET %s")
        cursor.execute(sql, w_params + h_params + [limit, offset])
        return cursor.fetchall()

    @with_cursor
    def count_filtered(self, cursor, q=None, precio_min=None, precio_max=None,
                       max_min=None, max_max=None):
        f_where = FilterBuilder()
        f_where.unaccent_ilike_any(["c.nombre", "c.nombre_en"], q)
        f_where.gte("c.precio", precio_min)
        f_where.lte("c.precio", precio_max)
        where, w_params = f_where.where()
        f_hav = FilterBuilder()
        f_hav.gte("(c.max_alumnos - COUNT(m.alumno_id))", max_min)
        f_hav.lte("(c.max_alumnos - COUNT(m.alumno_id))", max_max)
        having, h_params = f_hav.having()
        inner = SELECT_CURSOS_FILTER_BASE + where + SELECT_CURSOS_FILTER_GROUP + having
        cursor.execute(f"SELECT COUNT(*) FROM ({inner}) sub", w_params + h_params)
        row = cursor.fetchone()
        return row[0] if row else 0

    @with_transactions
    def insert_one_course(self, cursor, curso: Cursos):
        params = (curso.id, curso.nombre, curso.nombre_en, curso.profesor_id, curso.precio, curso.max_alumnos)
        cursor.execute(INSERT_CURSOS, params)
        print(f"Se ha ingresado el curso: {curso} dentro de la base de datos")

    @with_transactions
    def update_settings(self, cursor, curso_id: str, precio: float, max_alumnos: int, nombre_en: str = ""):
        cursor.execute(UPDATE_CURSO_SETTINGS, (nombre_en, precio, max_alumnos, curso_id))

    @with_transactions
    def delete_by_id(self, cursor, curso_id: str):
        cursor.execute(DELETE_CURSO, (curso_id,))

# Operaciones de la matricula
class OperacionesMatricula():
    @with_cursor
    def get_count(self, cursor):
        cursor.execute(COUNT_MATRICULAS)
        result = cursor.fetchone()
        return result[0] if result else 0

    @with_cursor
    def get_all_enrollments(self, cursor):
        try:
            cursor.execute(SELECT_ALL_MATRICULAS)
            return cursor.fetchall()
        except (Exception, Error) as e:
            print("Error al obtener las matrículas:", e)
            return []

    @with_cursor
    def get_all_enrollments_full(self, cursor):
        try:
            cursor.execute(SELECT_MATRICULAS_FULL)
            return cursor.fetchall()
        except (Exception, Error) as e:
            print("Error al obtener las matrículas:", e)
            return []

    @with_cursor
    def check_exists(self, cursor, alumno_id: str, curso_id: str) -> bool:
        try:
            cursor.execute(CHECK_MATRICULA_EXISTS, (alumno_id, curso_id))
            return cursor.fetchone() is not None
        except (Exception, Error) as e:
            print("Error al verificar matrícula:", e)
            return False

    @with_transactions
    def insert_one_enrollment(self, cursor, matricula: Matriculas):
        params = (matricula.alumno_id, matricula.curso_id, matricula.created_at)
        cursor.execute(INSERT_MATRICULAS, params)

    @with_cursor
    def get_filtered(self, cursor, q=None, fecha_desde=None, fecha_hasta=None,
                     limit=20, offset=0):
        f = FilterBuilder()
        f.ilike_any(["a.nombre", "c.nombre"], q)
        f.gte("DATE(m.created_at)", fecha_desde)
        f.lte("DATE(m.created_at)", fecha_hasta)
        where, params = f.where()
        sql = SELECT_MATRICULAS_FILTER_BASE + where + SELECT_MATRICULAS_FILTER_TAIL + " LIMIT %s OFFSET %s"
        cursor.execute(sql, params + [limit, offset])
        return cursor.fetchall()

    @with_cursor
    def count_filtered(self, cursor, q=None, fecha_desde=None, fecha_hasta=None):
        f = FilterBuilder()
        f.ilike_any(["a.nombre", "c.nombre"], q)
        f.gte("DATE(m.created_at)", fecha_desde)
        f.lte("DATE(m.created_at)", fecha_hasta)
        where, params = f.where()
        inner = ("SELECT m.alumno_id FROM matriculas m "
                 "JOIN alumnos a ON m.alumno_id=a.id "
                 "JOIN cursos c ON m.curso_id=c.id " + where)
        cursor.execute(f"SELECT COUNT(*) FROM ({inner}) sub", params)
        row = cursor.fetchone()
        return row[0] if row else 0

    @with_transactions
    def delete_enrollment(self, cursor, alumno_id: str, curso_id: str):
        cursor.execute(DELETE_MATRICULA, (alumno_id, curso_id))

    @with_connection
    def matricular_transaccional(self, conn, cur, alumno_id: str, curso_id: str, usuario: str = "anónimo"):
        """
        Proceso de matriculación completo en una única transacción ACID.
        Usa el decorador @with_connection para obtener conn+cursor con autocommit=False.
        Comprueba saldo, plazas y duplicados con bloqueo FOR UPDATE.
        Devuelve dict con 'ok', 'steps' y datos resultado.
        """
        import datetime

        def step(kind, text):
            return {"type": kind, "text": text}

        steps = []
        try:
            steps.append(step("info", "BEGIN;"))

            cur.execute(SELECT_ALUMNO_FOR_ENROLL, (alumno_id,))
            alumno = cur.fetchone()
            if not alumno:
                raise Exception("Alumno no encontrado en la base de datos.")
            a_id, a_nombre, a_saldo = alumno
            steps.append(step("ok", f"  SELECT … FROM alumnos WHERE id='{str(a_id)[:8]}…' FOR UPDATE;"))
            steps.append(step("ok", f"  -- {a_nombre}: saldo actual = {float(a_saldo):.2f} €"))

            cur.execute(SELECT_CURSO_FOR_ENROLL, (curso_id,))
            curso = cur.fetchone()
            if not curso:
                raise Exception("Asignatura no encontrada en la base de datos.")
            c_id, c_nombre, c_precio, c_max, c_inscritos = curso
            c_precio    = float(c_precio)
            c_inscritos = int(c_inscritos)
            steps.append(step("ok", f"  SELECT … FROM cursos WHERE id='{str(c_id)[:8]}…' FOR UPDATE;"))
            steps.append(step("ok", f"  -- {c_nombre}: precio={c_precio:.2f} €, plazas={c_inscritos}/{c_max}"))

            cur.execute(CHECK_MATRICULA_EXISTS, (alumno_id, curso_id))
            if cur.fetchone():
                raise Exception(f"ERROR 23505: El alumno ya está matriculado en «{c_nombre}» (PK duplicada).")

            if c_inscritos >= c_max:
                raise Exception(f"Sin plazas disponibles: {c_inscritos}/{c_max} ocupadas.")

            a_saldo = float(a_saldo)
            if a_saldo < c_precio:
                raise Exception(f"Saldo insuficiente: {a_saldo:.2f} € < {c_precio:.2f} € (precio asignatura).")

            steps.append(step("info", f"  UPDATE alumnos SET saldo = saldo - {c_precio:.2f} WHERE id = '…';"))
            cur.execute(UPDATE_ALUMNO_SALDO, (-c_precio, alumno_id))
            nuevo_saldo = a_saldo - c_precio
            steps.append(step("ok", f"  -- Saldo actualizado: {a_saldo:.2f} → {nuevo_saldo:.2f} €  ✓"))

            now = datetime.datetime.now(datetime.timezone.utc)
            steps.append(step("info", "  INSERT INTO matriculas (alumno_id, curso_id, created_at) VALUES (…);"))
            cur.execute(INSERT_MATRICULAS, (alumno_id, curso_id, now))
            steps.append(step("ok", f"  -- Matrícula registrada en {now.strftime('%Y-%m-%d %H:%M:%S UTC')}  ✓"))

            cur.execute(INSERT_AUDITORIA, (usuario, "CREATE", "matricula", str(alumno_id),
                                           f"Matrícula transaccional: {a_nombre} → {c_nombre}"))

            conn.commit()
            steps.append(step("ok", "COMMIT;"))
            steps.append(step("ok", f"  -- Transacción completada con éxito. Nuevo saldo: {nuevo_saldo:.2f} €  ✓"))

            return {
                "ok": True,
                "steps": steps,
                "alumno": a_nombre,
                "curso": c_nombre,
                "precio": c_precio,
                "saldo_anterior": a_saldo,
                "saldo_nuevo": nuevo_saldo,
            }

        except Exception as e:
            conn.rollback()
            steps.append(step("error", f"  {e}"))
            steps.append(step("warn",  "ROLLBACK;"))
            steps.append(step("warn",  "  -- Ningún cambio fue persistido. Integridad conservada.  ✓"))
            return {"ok": False, "steps": steps, "error": str(e)}


# Operaciones de Auditoría
class OperacionesAuditoria():
    @with_transactions
    def registrar(self, cursor, usuario: str, accion: str, entidad: str, entidad_id: str, detalle: str):
        cursor.execute(INSERT_AUDITORIA, (usuario, accion, entidad, entidad_id, detalle))

    @with_cursor
    def get_all(self, cursor):
        try:
            cursor.execute(SELECT_ALL_AUDITORIA)
            return cursor.fetchall()
        except (Exception, Error) as e:
            print("Error al obtener auditoría:", e)
            return []

    @with_cursor
    def get_filtered(self, cursor, q=None, accion=None, entidad=None,
                     fecha_desde=None, fecha_hasta=None, limit=20, offset=0):
        f = FilterBuilder()
        f.ilike_any(["usuario", "detalle"], q)
        f.eq("accion", accion)
        f.eq("entidad", entidad)
        f.gte("DATE(created_at)", fecha_desde)
        f.lte("DATE(created_at)", fecha_hasta)
        where, params = f.where()
        sql = SELECT_AUDITORIA_FILTER_BASE + where + SELECT_AUDITORIA_FILTER_TAIL + " LIMIT %s OFFSET %s"
        cursor.execute(sql, params + [limit, offset])
        return cursor.fetchall()

    @with_cursor
    def count_filtered(self, cursor, q=None, accion=None, entidad=None,
                       fecha_desde=None, fecha_hasta=None):
        f = FilterBuilder()
        f.ilike_any(["usuario", "detalle"], q)
        f.eq("accion", accion)
        f.eq("entidad", entidad)
        f.gte("DATE(created_at)", fecha_desde)
        f.lte("DATE(created_at)", fecha_hasta)
        where, params = f.where()
        cursor.execute("SELECT COUNT(*) FROM auditoria" + where, params)
        row = cursor.fetchone()
        return row[0] if row else 0

    @with_cursor
    def get_count(self, cursor):
        cursor.execute(COUNT_AUDITORIA)
        result = cursor.fetchone()
        return result[0] if result else 0

    @with_transactions
    def delete_by_id(self, cursor, audit_id: int):
        cursor.execute(DELETE_AUDITORIA, (audit_id,))

    @with_transactions
    def delete_all(self, cursor):
        cursor.execute(DELETE_ALL_AUDITORIA)

    @with_transactions
    def create_table(self, cursor):
        cursor.execute(CREATE_AUDITORIA)
        cursor.execute(CREATE_INDEX_AUDITORIA_ENTIDAD)


# Vista: alumno / profesor / asignatura
class OperacionesVista():

    @with_cursor
    def get_all(self, cursor):
        try:
            cursor.execute(SELECT_VISTA_MATRICULAS)
            return cursor.fetchall()
        except (Exception, Error) as e:
            print("Error al consultar la vista:", e)
            return []

    @with_cursor
    def get_count(self, cursor):
        cursor.execute(COUNT_VISTA_MATRICULAS)
        result = cursor.fetchone()
        return result[0] if result else 0

    @with_cursor
    def get_filtered(self, cursor, q=None, fecha_desde=None, fecha_hasta=None,
                     limit=20, offset=0):
        f = FilterBuilder()
        f.ilike_any(["alumno", "profesor", "asignatura"], q)
        f.gte("DATE(created_at)", fecha_desde)
        f.lte("DATE(created_at)", fecha_hasta)
        where, params = f.where()
        sql = SELECT_VISTA_FILTER_BASE + where + " " + SELECT_VISTA_FILTER_TAIL + " LIMIT %s OFFSET %s"
        cursor.execute(sql, params + [limit, offset])
        return cursor.fetchall()

    @with_cursor
    def count_filtered(self, cursor, q=None, fecha_desde=None, fecha_hasta=None):
        f = FilterBuilder()
        f.ilike_any(["alumno", "profesor", "asignatura"], q)
        f.gte("DATE(created_at)", fecha_desde)
        f.lte("DATE(created_at)", fecha_hasta)
        where, params = f.where()
        cursor.execute("SELECT COUNT(*) FROM vista_matriculas_detalle" + where, params)
        row = cursor.fetchone()
        return row[0] if row else 0



class OperacionesAnalitica():
    @with_cursor
    def get_filter(self, cursor):
        cursor.execute(SELECT_ANALITICA_FILTER)
        return cursor.fetchall()

    @with_cursor
    def get_rollup(self, cursor):
        cursor.execute(SELECT_ANALITICA_ROLLUP)
        return cursor.fetchall()

    @with_cursor
    def get_grouping_sets(self, cursor):
        cursor.execute(SELECT_ANALITICA_GROUPING_SETS)
        return cursor.fetchall()

    @with_cursor
    def get_row_number(self, cursor):
        cursor.execute(SELECT_ANALITICA_ROW_NUMBER)
        return cursor.fetchall()
