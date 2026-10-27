import pytest

import mpt.database as db


@pytest.fixture
def temp_db(tmp_path, monkeypatch):
    """Redirect every path the module touches to a pytest temp dir."""
    monkeypatch.setattr(db.settings, "BASE_PATH", tmp_path)
    monkeypatch.setattr(db.settings, "DB_PATH", tmp_path / "test.db")
    monkeypatch.setattr(db.settings, "EXPORT_PATH", tmp_path / "export")
    return db.settings