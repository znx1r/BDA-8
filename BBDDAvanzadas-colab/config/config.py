from configparser import ConfigParser
import os
from pathlib import Path

class Config():
    # Lectura de la configuración y obtención de credenciales
    def __init__(self):
        self.config = ConfigParser()
        self.config.read(Path(__file__).resolve().parent / "database.ini")
        
    # Obtener valores de la configuracion de la base de datos
    def get_postgresql_values(self) -> dict:
        postgresql_config = self.config['postgresql']

        return {
            "DATABASE_HOST": postgresql_config['host'],
            "DATABASE_NAME": postgresql_config['database'],
            "DATABASE_USER":postgresql_config['user'],
            "DATABASE_PASSWORD":postgresql_config['password'],
            "DATABASE_PORT":int(postgresql_config['port']),
        }

    # Obtener valores para la configuración del servidor
    def get_server_values(self) -> dict:
        server_config = self.config["server"]

        return {
            "SERVER_IP": server_config['server_ip'],
            "SERVER_PORT": int(server_config['server_port']),
            "TEMPLATE_DIR": server_config['template_dir'],
        }

    # Obtener valores para la configuración de la aplicación
    def get_app_values(self) -> dict:
        app_config = self.config["app"]

        return {
            "PAGE_SIZE": int(app_config['page_size']),
        }
