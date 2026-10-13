"""Tests cho SQLite + bảng bids (data_model.md §2, BR-09)."""

from __future__ import annotations

from datetime import date

from sqlalchemy import inspect

from app.core import db
from app.models import Bid


def test_init_db_creates_bids_table():
    db.init_db()
    inspector = inspect(db.engine)

    assert "bids" in inspector.get_table_names()

    columns = {col["name"]: col for col in inspector.get_columns("bids")}
    assert "status" in columns
    assert "locked" in columns
    assert "customer_language" in columns
    assert "display_currency" in columns

    # status CHECK chứa 'draft' (máy trạng thái data_model.md §18).
    checks = {c["name"]: c["sqltext"] for c in inspector.get_check_constraints("bids")}
    assert "ck_bids_status" in checks
    assert "'draft'" in checks["ck_bids_status"]

    # locked DEFAULT 0.
    assert columns["locked"]["default"] == "0"


def test_migrate_adds_not_null_column_with_server_default(tmp_path, monkeypatch):
    """Schema drift: cột NOT NULL có server_default được ALTER thêm vào bảng cũ (BR-09)."""
    from sqlalchemy import create_engine, inspect

    from app.core import db

    url = f"sqlite:///{tmp_path / 'drift.db'}"
    engine = create_engine(url, connect_args={"check_same_thread": False})
    monkeypatch.setattr(db, "engine", engine)

    # Mô phỏng DB cũ: bảng quotations thiếu cột price_to_win_percent.
    with engine.begin() as conn:
        conn.exec_driver_sql(
            "CREATE TABLE quotations ("
            "id INTEGER PRIMARY KEY, "
            "bid_id INTEGER NOT NULL, "
            "contract_model VARCHAR(30) NOT NULL, "
            "contingency_percent FLOAT NOT NULL, "
            "onsite_percent FLOAT, "
            "tm_months INTEGER, "
            "odc_fte FLOAT, "
            "odc_months INTEGER, "
            "fx_rate_value FLOAT NOT NULL, "
            "fx_rate_date DATE NOT NULL, "
            "totals JSON NOT NULL, "
            "valid_until DATE, "
            "tax_mode VARCHAR(20) NOT NULL, "
            "rounding_note VARCHAR(200), "
            "reference_snapshot_id INTEGER NOT NULL, "
            "computed_at DATETIME NOT NULL, "
            "computed_by VARCHAR(100)"
            ")"
        )

    db.init_db()

    inspector = inspect(engine)
    columns = {col["name"]: col for col in inspector.get_columns("quotations")}
    assert "price_to_win_percent" in columns
    assert columns["price_to_win_percent"]["default"] == "0"


def test_migrate_adds_json_not_null_column_with_server_default(tmp_path, monkeypatch):
    """Cột JSON NOT NULL có server_default ('[]'/'{}') được thêm vào bảng cũ."""
    from sqlalchemy import create_engine, inspect
    from sqlalchemy.orm import sessionmaker

    from app.core import db

    url = f"sqlite:///{tmp_path / 'drift2.db'}"
    engine = create_engine(url, connect_args={"check_same_thread": False})
    session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    monkeypatch.setattr(db, "engine", engine)
    monkeypatch.setattr(db, "SessionLocal", session_local)

    with engine.begin() as conn:
        conn.exec_driver_sql(
            "CREATE TABLE solution_choices ("
            "id INTEGER PRIMARY KEY, "
            "bid_id INTEGER NOT NULL, "
            "direction VARCHAR(30) NOT NULL, "
            "reason_vi TEXT NOT NULL, "
            "risks_vi JSON NOT NULL, "
            "architecture_notes_vi TEXT, "
            "reliability_vi TEXT, "
            "feasibility_score JSON, "
            "chosen_by VARCHAR(100), "
            "chosen_at DATETIME NOT NULL, "
            "superseded_at DATETIME"
            ")"
        )
        conn.exec_driver_sql(
            "INSERT INTO solution_choices (id, bid_id, direction, reason_vi, risks_vi, chosen_at) "
            "VALUES (1, 1, 'build', 'lý do', '[]', '2026-10-11 10:00:00')"
        )

    db.init_db()

    inspector = inspect(engine)
    columns = {col["name"]: col for col in inspector.get_columns("solution_choices")}
    assert "assumptions_vi" in columns
    assert "excluded_directions" in columns
    assert "feasibility" in columns

    from app.models import SolutionChoice

    session = db.SessionLocal()
    try:
        row = session.get(SolutionChoice, 1)
        assert row is not None
        assert row.assumptions_vi == []
        assert row.excluded_directions == []
        assert row.feasibility == {}
    finally:
        session.close()


def test_rebuild_table_fixes_stale_check_constraint(tmp_path, monkeypatch):
    """CHECK constraint lệch (thiếu 'error') được rebuild, giữ nguyên dữ liệu."""
    from datetime import date

    from sqlalchemy import create_engine, inspect, text
    from sqlalchemy.orm import sessionmaker

    from app.core import db

    url = f"sqlite:///{tmp_path / 'drift3.db'}"
    engine = create_engine(url, connect_args={"check_same_thread": False})
    session_local = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    monkeypatch.setattr(db, "engine", engine)
    monkeypatch.setattr(db, "SessionLocal", session_local)

    with engine.begin() as conn:
        conn.exec_driver_sql(
            "CREATE TABLE bids ("
            "id INTEGER NOT NULL PRIMARY KEY, "
            "project_name VARCHAR(255) NOT NULL, "
            "customer_name VARCHAR(255) NOT NULL, "
            "submission_deadline DATE NOT NULL, "
            "customer_language VARCHAR(10) NOT NULL, "
            "request_content TEXT NOT NULL, "
            "status VARCHAR(30) DEFAULT 'draft' NOT NULL, "
            "created_by VARCHAR(100) NOT NULL, "
            "created_at DATETIME NOT NULL, "
            "updated_at DATETIME NOT NULL, "
            "CONSTRAINT ck_bids_status CHECK (status IN ('draft','waiting_clarification'))"
            ")"
        )
        conn.exec_driver_sql(
            "INSERT INTO bids (id, project_name, customer_name, submission_deadline, "
            "customer_language, request_content, status, created_by, created_at, updated_at) "
            "VALUES (1, 'Dự án cũ (giả lập)', 'Công ty Cũ (giả lập)', '2026-12-15', 'vi', "
            "'Yêu cầu cũ.', 'draft', 'Nhu', '2026-10-11 10:00:00', '2026-10-11 10:00:00')"
        )

    db.init_db()

    with engine.begin() as conn:
        conn.exec_driver_sql("UPDATE bids SET status='error' WHERE id=1")

    inspector = inspect(engine)
    checks = {c["name"]: c["sqltext"] for c in inspector.get_check_constraints("bids")}
    assert "'error'" in checks["ck_bids_status"]

    from app.models import Bid

    session = db.SessionLocal()
    try:
        row = session.get(Bid, 1)
        assert row is not None
        assert row.project_name == "Dự án cũ (giả lập)"
        assert row.status == "error"
    finally:
        session.close()

    # Idempotent: chạy lại init_db không lỗi, dữ liệu vẫn còn.
    db.init_db()
    session = db.SessionLocal()
    try:
        assert session.get(Bid, 1) is not None
    finally:
        session.close()


def test_insert_and_read_bid():
    db.init_db()
    session = db.SessionLocal()
    try:
        bid = Bid(
            project_name="Hệ thống CRM khách hàng ABC (giả lập)",
            customer_name="Công ty XYZ (giả lập)",
            submission_deadline=date(2026, 12, 15),
            customer_language="ja",
            request_content="Yêu cầu xây dựng hệ thống CRM (dữ liệu giả lập).",
            created_by="Nhu",
        )
        session.add(bid)
        session.commit()

        loaded = session.get(Bid, bid.id)
        assert loaded is not None
        assert loaded.project_name == "Hệ thống CRM khách hàng ABC (giả lập)"
        assert loaded.customer_language == "ja"
        assert loaded.status == "draft"
        assert loaded.locked is False
        assert loaded.no_requirement_file is False
        assert loaded.display_currency == "VND"
        assert loaded.created_at is not None
        assert loaded.updated_at is not None
    finally:
        session.close()