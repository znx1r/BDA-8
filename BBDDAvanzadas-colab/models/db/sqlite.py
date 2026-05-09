from werkzeug.security import check_password_hash
from .decorators import with_sqlite
from .querys import SELECT_USUARIO_BY_USERNAME


class Sqlite:
    @with_sqlite
    def get_user_by_username(self, cursor, username: str):
        cursor.execute(SELECT_USUARIO_BY_USERNAME, (username,))
        return cursor.fetchone()

    def verify_password(self, username: str, password: str) -> bool:
        user = self.get_user_by_username(username)
        if not user:
            return False
        return check_password_hash(user["password_hash"], password)
