"""
Utilidad para construir cláusulas WHERE y HAVING dinámicas de forma segura.

Uso:
    conds = FilterBuilder()
    conds.ilike("a.nombre", q)
    conds.gte("a.saldo", saldo_min)
    conds.lte("a.saldo", saldo_max)
    where_sql, params = conds.where()
"""


class FilterBuilder:
    def __init__(self):
        self._parts: list[tuple[str, list]] = []

    def ilike(self, column: str, value: str | None):
        if value:
            self._parts.append((f"{column} ILIKE %s", [f"%{value}%"]))

    def ilike_any(self, columns: list[str], value: str | None):
        """value ILIKE any of the columns (OR)."""
        if value:
            clause = "(" + " OR ".join(f"{c} ILIKE %s" for c in columns) + ")"
            self._parts.append((clause, [f"%{value}%" for _ in columns]))

    def unaccent_ilike_any(self, columns: list[str], value: str | None):
        """unaccent(col) ILIKE unaccent(value) for any of the columns (OR) — accent-insensitive search."""
        if value:
            clause = "(" + " OR ".join(f"unaccent({c}) ILIKE unaccent(%s)" for c in columns) + ")"
            self._parts.append((clause, [f"%{value}%" for _ in columns]))

    def eq(self, column: str, value):
        if value not in (None, ""):
            self._parts.append((f"{column} = %s", [value]))

    def gte(self, column: str, value):
        if value is not None:
            self._parts.append((f"{column} >= %s", [value]))

    def lte(self, column: str, value):
        if value is not None:
            self._parts.append((f"{column} <= %s", [value]))

    def _build(self, keyword: str) -> tuple[str, list]:
        if not self._parts:
            return "", []
        sql    = f" {keyword} " + " AND ".join(p for p, _ in self._parts)
        params = [v for _, vals in self._parts for v in vals]
        return sql, params

    def where(self) -> tuple[str, list]:
        return self._build("WHERE")

    def having(self) -> tuple[str, list]:
        return self._build("HAVING")

    def has_filters(self) -> bool:
        return bool(self._parts)
