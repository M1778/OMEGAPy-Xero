import os
import sys
import sqlite3
import datetime
import tempfile
import pytest

_SOREUI_DIR = os.path.join(os.path.dirname(__file__), "..", "SoreUI")
_BASE_PY = os.path.join(_SOREUI_DIR, "base.py")


def _load_manage_database_class():
    """Import ManageDatabase without triggering module-level DB creation."""
    with open(_BASE_PY) as f:
        source = f.read()
    # Extract just the ManageDatabase class definition
    lines = source.split("\n")
    in_class = False
    class_lines = []
    for line in lines:
        if line.startswith("class ManageDatabase"):
            in_class = True
        if in_class:
            class_lines.append(line)
            # Stop at next top-level definition or end of class
            if len(class_lines) > 1 and line and not line.startswith(" ") and not line.startswith("\t") and not line.startswith("#"):
                class_lines.pop()
                break
    class_source = "\n".join(class_lines)
    ns = {"sqlite3": sqlite3}
    exec(class_source, ns)
    return ns["ManageDatabase"]


ManageDatabase = _load_manage_database_class()


# ---------------------------------------------------------------------------
# base.py – ManageDatabase
# ---------------------------------------------------------------------------

class TestManageDatabase:
    def test_context_manager(self, tmp_path):
        db_path = str(tmp_path / "test.db")
        with ManageDatabase(db_path) as db:
            db.query("CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT)")
            db.query_f("INSERT INTO test (name) VALUES (?)", [("hello",)])
            db.commit()
            result = db.fetchall("SELECT * FROM test")
            assert len(result) == 1
            assert result[0][1] == "hello"

    def test_reconnect(self, tmp_path):
        db_path = str(tmp_path / "test2.db")
        db = ManageDatabase(db_path)
        db.reconnect(str(tmp_path / "test3.db"))
        db.query("CREATE TABLE test (id INTEGER)")
        db.commit()
        db.disconnect()

    def test_query_and_fetchall(self, tmp_path):
        db_path = str(tmp_path / "test4.db")
        db = ManageDatabase(db_path)
        db.query("CREATE TABLE items (name TEXT)")
        db.query_f("INSERT INTO items (name) VALUES (?)", [("a",), ("b",), ("c",)])
        db.commit()
        rows = db.fetchall("SELECT * FROM items")
        assert len(rows) == 3
        db.disconnect()


# ---------------------------------------------------------------------------
# base.py – SQLite types are valid (read file directly, no import)
# ---------------------------------------------------------------------------

class TestSQLSchema:
    def test_schema_has_valid_sqlite_types(self):
        with open(_BASE_PY) as f:
            content = f.read()
        for keyword in ["varchar", "MEDIUMTEXT"]:
            assert keyword not in content, f"Non-SQLite type '{keyword}' still in base.py"

    def test_admin_uses_random_password(self):
        with open(_BASE_PY) as f:
            content = f.read()
        assert "secrets.choice" in content, "base.py should use secrets.choice for admin password"
        assert "string.ascii_letters" in content, "base.py should use string.ascii_letters for password charset"


# ---------------------------------------------------------------------------
# base.py – deprecated utcnow fix
# ---------------------------------------------------------------------------

class TestDatetimeFix:
    def test_no_utcnow_in_base(self):
        with open(os.path.join(os.path.dirname(__file__), "..", "SoreUI", "base.py")) as f:
            content = f.read()
        assert "utcnow()" not in content, "deprecated utcnow() still present in base.py"


# ---------------------------------------------------------------------------
# fontuse.py – PyQt5 → PyQt6
# ---------------------------------------------------------------------------

class TestFontuseCompat:
    def test_no_pyqt5_imports(self):
        path = os.path.join(os.path.dirname(__file__), "..", "SoreUI", "files", "fontuse.py")
        with open(path) as f:
            content = f.read()
        assert "PyQt5" not in content, "PyQt5 imports still present in fontuse.py!"

    def test_uses_pyqt6(self):
        path = os.path.join(os.path.dirname(__file__), "..", "SoreUI", "files", "fontuse.py")
        with open(path) as f:
            content = f.read()
        assert "PyQt6" in content, "fontuse.py should use PyQt6"

    def test_no_exec_underscore(self):
        """PyQt6 uses app.exec() not app.exec_()"""
        path = os.path.join(os.path.dirname(__file__), "..", "SoreUI", "files", "fontuse.py")
        with open(path) as f:
            content = f.read()
        assert "exec_()" not in content, "fontuse.py still uses deprecated exec_()"


# ---------------------------------------------------------------------------
# main.py – no breakpoints
# ---------------------------------------------------------------------------

class TestMainPy:
    def test_debug_method_no_breakpoint(self):
        path = os.path.join(os.path.dirname(__file__), "..", "SoreUI", "files", "main.py")
        with open(path) as f:
            content = f.read()
        # The debug() method should not call breakpoint()
        assert "breakpoint()" not in content, "main.py still has breakpoint()!"

    def test_no_junk_comments(self):
        path = os.path.join(os.path.dirname(__file__), "..", "SoreUI", "files", "main.py")
        with open(path) as f:
            content = f.read()
        assert "KMS" not in content, "Junk comments still in main.py"


# ---------------------------------------------------------------------------
# Dead code files marked as unused
# ---------------------------------------------------------------------------

class TestDeadCodeMarked:
    def test_checkpoint_marked_unused(self):
        path = os.path.join(os.path.dirname(__file__), "..", "SoreUI", "files", "checkpoint.py")
        with open(path) as f:
            first_line = f.readline()
        assert "UNUSED" in first_line or "unused" in first_line.lower(), \
            "checkpoint.py should be marked as unused"

    def test_bmain_marked_unused(self):
        path = os.path.join(os.path.dirname(__file__), "..", "SoreUI", "files", "bmain.py")
        with open(path) as f:
            first_line = f.readline()
        assert "UNUSED" in first_line or "unused" in first_line.lower(), \
            "bmain.py should be marked as unused"

    def test_fontuse_marked_unused(self):
        path = os.path.join(os.path.dirname(__file__), "..", "SoreUI", "files", "fontuse.py")
        with open(path) as f:
            first_line = f.readline()
        assert "UNUSED" in first_line or "unused" in first_line.lower(), \
            "fontuse.py should be marked as unused"


# ---------------------------------------------------------------------------
# requirements.txt – sanity
# ---------------------------------------------------------------------------

class TestRequirements:
    def test_requirements_not_huge(self):
        path = os.path.join(os.path.dirname(__file__), "..", "requirements.txt")
        with open(path) as f:
            lines = [l.strip() for l in f if l.strip() and not l.startswith("#")]
        assert len(lines) < 100, f"requirements.txt has {len(lines)} packages, expected <100"

    def test_flask_in_requirements(self):
        path = os.path.join(os.path.dirname(__file__), "..", "requirements.txt")
        with open(path) as f:
            content = f.read()
        assert "flask" in content.lower()

    def test_openai_in_requirements(self):
        path = os.path.join(os.path.dirname(__file__), "..", "requirements.txt")
        with open(path) as f:
            content = f.read()
        assert "openai" in content.lower()


# ---------------------------------------------------------------------------
# pyproject.toml exists
# ---------------------------------------------------------------------------

class TestPyproject:
    def test_pyproject_exists(self):
        path = os.path.join(os.path.dirname(__file__), "..", "pyproject.toml")
        assert os.path.exists(path), "pyproject.toml not found"

    def test_pyproject_has_project_section(self):
        path = os.path.join(os.path.dirname(__file__), "..", "pyproject.toml")
        with open(path) as f:
            content = f.read()
        assert "[project]" in content or "[project " in content


# ---------------------------------------------------------------------------
# .gitignore exists
# ---------------------------------------------------------------------------

class TestGitignore:
    def test_gitignore_exists(self):
        path = os.path.join(os.path.dirname(__file__), "..", ".gitignore")
        assert os.path.exists(path), ".gitignore not found"

    def test_gitignore_covers_venv(self):
        path = os.path.join(os.path.dirname(__file__), "..", ".gitignore")
        with open(path) as f:
            content = f.read()
        assert ".venv" in content or "venv" in content

    def test_gitignore_covers_pycache(self):
        path = os.path.join(os.path.dirname(__file__), "..", ".gitignore")
        with open(path) as f:
            content = f.read()
        assert "__pycache__" in content


# ---------------------------------------------------------------------------
# failed_requirements.txt deleted
# ---------------------------------------------------------------------------

class TestObsoleteFiles:
    def test_failed_requirements_deleted(self):
        path = os.path.join(os.path.dirname(__file__), "..", "failed_requirements.txt")
        assert not os.path.exists(path), "failed_requirements.txt should have been deleted"
