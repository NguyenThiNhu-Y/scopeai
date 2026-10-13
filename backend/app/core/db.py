"""Kết nối SQLite (SQLAlchemy 2.0) — engine, session, Base, init_db.

Migration M1 dùng ``Base.metadata.create_all()`` (KHÔNG Alembic — BR-09).
"""

from __future__ import annotations

import os
import re

from sqlalchemy import CheckConstraint, create_engine, text
from sqlalchemy.engine import Engine, URL
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.schema import CreateIndex, CreateTable

from app.core.config import settings


class Base(DeclarativeBase):
    """Base class cho mọi ORM model."""


def _create_engine(database_url: str) -> Engine:
    connect_args = {}
    if database_url.startswith("sqlite"):
        # SQLite + FastAPI/TestClient chạy đa luồng — cần tắt check_same_thread.
        connect_args["check_same_thread"] = False
    return create_engine(database_url, connect_args=connect_args)


engine = _create_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def _ensure_sqlite_dir(url: URL) -> None:
    """Tạo thư mục chứa file SQLite nếu chưa tồn tại (tương đối hoặc tuyệt đối)."""
    if url.drivername != "sqlite":
        return
    db_path = url.database
    if not db_path or db_path == ":memory:":
        return
    parent = os.path.dirname(db_path)
    if parent:
        os.makedirs(parent, exist_ok=True)


def _server_default_sql(col) -> str | None:
    """Trích SQL fragment từ ``server_default`` (chuỗi hoặc ``text(...)``)."""
    sd = col.server_default
    if sd is None:
        return None
    arg = getattr(sd, "arg", None)
    if isinstance(arg, str):
        return arg
    text_arg = getattr(arg, "text", None)
    if isinstance(text_arg, str):
        return text_arg
    return None


def _migrate_sqlite_schema() -> None:
    """Reconcile schema drift trên bảng SQLite đã tồn tại (BR-09: chỉ create_all).

    ``create_all`` tạo bảng mới nhưng KHÔNG alter bảng cũ — DB tạo bởi phiên bản
    model cũ bị thiếu cột (vd: ``attachments.original_path``, ``quotations.price_to_win_percent``)
    → mọi SELECT theo model lỗi 500. Thêm cột còn thiếu: cột nullable thêm trực tiếp;
    cột NOT NULL chỉ thêm khi có ``server_default`` (ALTER ADD COLUMN an toàn với dữ
    liệu có sẵn vì SQLite áp default cho hàng cũ).
    """
    if not engine.url.drivername.startswith("sqlite"):
        return
    with engine.begin() as conn:
        for table in Base.metadata.sorted_tables:
            existing = {
                row[1]
                for row in conn.exec_driver_sql(
                    f'PRAGMA table_info("{table.name}")'
                ).fetchall()
            }
            for col in table.columns:
                if col.name in existing:
                    continue
                col_type = col.type.compile(engine.dialect)
                default = ""
                if col.name == "customer_language":
                    default = " DEFAULT 'vi'"
                elif col.name == "translations":
                    default = " DEFAULT '{}'"
                elif col.name == "sent_at":
                    default = " DEFAULT NULL"
                elif col.name == "sent_note":
                    default = " DEFAULT NULL"
                elif col.nullable is False:
                    server_default = _server_default_sql(col)
                    if server_default is None:
                        continue
                    default = f" DEFAULT {server_default}"
                conn.exec_driver_sql(
                    f'ALTER TABLE "{table.name}" ADD COLUMN "{col.name}" {col_type}{default}'
                )


def _extract_check_body(ddl: str, name: str) -> str | None:
    """Trích nội dung CHECK constraint theo tên từ DDL (xử lý paren lồng nhau)."""
    m = re.search(rf'CONSTRAINT\s+"?{re.escape(name)}"?\s+CHECK\s*\(', ddl, re.S)
    if m is None:
        return None
    start = m.end() - 1
    depth = 0
    for i in range(start, len(ddl)):
        ch = ddl[i]
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return ddl[start + 1 : i]
    return None


def _check_constraint_drift(conn, table) -> bool:
    """True nếu bảng trong DB có CHECK constraint cùng tên nhưng khác nội dung model."""
    row = conn.exec_driver_sql(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name=?",
        (table.name,),
    ).first()
    ddl = row[0] if row and row[0] else ""
    for constr in table.constraints:
        if not isinstance(constr, CheckConstraint) or not constr.name:
            continue
        db_text = _extract_check_body(ddl, constr.name)
        if db_text is None:
            continue
        if db_text.strip() != str(constr.sqltext).strip():
            return True
    return False


def _rebuild_table(conn, table) -> None:
    """Rebuild bảng theo DDL model hiện tại, giữ nguyên dữ liệu (cột chung).

    SQLite không hỗ trợ ALTER/DROP CONSTRAINT — drift CHECK (vd ``ck_bids_status``
    thiếu ``'error'``) chỉ sửa được bằng rebuild. DDL của SQLite là transactional nên
    nếu lỗi giữa chừng, transaction rollback trả về trạng thái cũ.
    """
    old = f"__{table.name}_old"
    conn.exec_driver_sql(f'ALTER TABLE "{table.name}" RENAME TO "{old}"')
    conn.exec_driver_sql(
        str(CreateTable(table).compile(dialect=engine.dialect))
    )
    for idx in table.indexes:
        conn.exec_driver_sql(str(CreateIndex(idx).compile(dialect=engine.dialect)))
    old_cols = {
        row[1]
        for row in conn.exec_driver_sql(f'PRAGMA table_info("{old}")').fetchall()
    }
    common = [c.name for c in table.columns if c.name in old_cols]
    cols_sql = ", ".join(f'"{c}"' for c in common)
    conn.exec_driver_sql(
        f'INSERT INTO "{table.name}" ({cols_sql}) SELECT {cols_sql} FROM "{old}"'
    )
    conn.exec_driver_sql(f'DROP TABLE "{old}"')


def _reconcile_check_constraints() -> None:
    """Rebuild bảng nào có CHECK constraint lệch với model (BR-09: không Alembic)."""
    if not engine.url.drivername.startswith("sqlite"):
        return
    with engine.begin() as conn:
        for table in Base.metadata.sorted_tables:
            if _check_constraint_drift(conn, table):
                _rebuild_table(conn, table)


def init_db() -> None:
    """Tạo toàn bộ bảng (create_all) — idempotent, không alter bảng cũ."""
    _ensure_sqlite_dir(engine.url)
    Base.metadata.create_all(bind=engine)
    _migrate_sqlite_schema()
    _reconcile_check_constraints()


def check_db() -> bool:
    """Kiểm tra kết nối DB bằng SELECT 1. Raise nếu lỗi."""
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return True
