import os
from config.config import Config

config = Config()
server_values = config.get_server_values()
postgresql_values = config.get_postgresql_values()
app_values = config.get_app_values()

# Importar la configuración del servidor
SERVER_IP = server_values["SERVER_IP"]
SERVER_PORT = server_values["SERVER_PORT"]
TEMPLATE_DIR = server_values["TEMPLATE_DIR"]

# Importar la configuración de la base de datos
PG_HOST = postgresql_values["DATABASE_HOST"]
PG_NAME = postgresql_values["DATABASE_NAME"]
PG_USER = postgresql_values["DATABASE_USER"]
PG_PASSWORD = postgresql_values["DATABASE_PASSWORD"]
PG_PORT = postgresql_values["DATABASE_PORT"]

# Importar la configuración de la aplicación
PAGE_SIZE = app_values["PAGE_SIZE"]

# Rutas de SQLite
BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SQLITE_PATH = os.path.join(BASE_DIR, "auth.db")
