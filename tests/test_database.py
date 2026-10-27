"""Smoke tests for mpt.database against a temporary SQLite DB."""

import pandas as pd
from sqlalchemy import inspect

import mpt.database as db


def _tables():
    return set(inspect(db.connect()).get_table_names())


def test_connect_uses_redirected_path(temp_db):
    engine = db.connect()
    assert str(engine.url).endswith("test.db")


def test_persist_creates_expected_tables(temp_db):
    db.persist()
    assert {"app_config", "diffusivity", "analysis_config"}.issubset(_tables())


def test_persist_is_idempotent(temp_db):
    db.persist()
    db.persist()  # second run must not raise or recreate
    assert "analysis_config" in _tables()