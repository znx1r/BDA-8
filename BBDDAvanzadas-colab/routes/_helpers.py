"""Utilidades compartidas por los blueprints de listado."""
from flask import request
from config import PAGE_SIZE


def _float(name, default=None):
    v = request.args.get(name, '').strip()
    try:
        return float(v) if v != '' else default
    except ValueError:
        return default


def _int(name, default=None):
    v = request.args.get(name, '').strip()
    try:
        return int(v) if v != '' else default
    except ValueError:
        return default


def _str(name):
    return request.args.get(name, '').strip() or None


def _date(name):
    return request.args.get(name, '').strip() or None


def paginate(filtered_count: int, page_size: int = PAGE_SIZE):
    page = max(1, request.args.get('page', 1, type=int))
    total_pages = max(1, -(-filtered_count // page_size))
    page = min(page, total_pages)
    offset = (page - 1) * page_size
    p_start = max(1, page - 2)
    p_end   = min(total_pages, p_start + 4)
    return {
        'page': page,
        'total_pages': total_pages,
        'offset': offset,
        'limit': page_size,
        'pages': list(range(p_start, p_end + 1)),
    }
