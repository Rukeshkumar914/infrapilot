import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from infrapilot.postgres_backup import (
    _validate_connection,
    backup_database,
    list_backups,
    restore_database,
    validate_backup,
)


def test_validate_connection_invalid_database():
    with pytest.raises(ValueError):
        _validate_connection("invalid-db", "localhost", 5432, "user", 30)


def test_validate_connection_invalid_port():
    with pytest.raises(ValueError):
        _validate_connection("test_db", "localhost", 70000, "user", 30)


def test_validate_connection_invalid_timeout():
    with pytest.raises(ValueError):
        _validate_connection("test_db", "localhost", 5432, "user", 0)


def test_list_backups(tmp_path):
    dump_file = tmp_path / "backup.dump"
    dump_file.write_bytes(b"test backup")

    (tmp_path / "notes.txt").write_text("not a backup")

    result = list_backups(tmp_path)

    assert len(result) == 1
    assert result[0]["filename"] == "backup.dump"
    assert result[0]["size_bytes"] == 11


def test_list_backups_missing_directory(tmp_path):
    missing_dir = tmp_path / "missing"

    with pytest.raises(FileNotFoundError):
        list_backups(missing_dir)


def test_validate_backup_success(tmp_path):
    backup_file = tmp_path / "backup.dump"
    backup_file.write_bytes(b"test backup")

    with patch("infrapilot.postgres_backup.subprocess.run") as mock_run:
        mock_run.return_value = subprocess.CompletedProcess(
            args=["pg_restore"],
            returncode=0,
            stdout="Archive listing",
            stderr="",
        )

        result = validate_backup(backup_file)

    assert result["valid"] is True
    assert result["returncode"] == 0


def test_validate_backup_invalid_archive(tmp_path):
    backup_file = tmp_path / "invalid.dump"
    backup_file.write_bytes(b"invalid data")

    with patch("infrapilot.postgres_backup.subprocess.run") as mock_run:
        mock_run.return_value = subprocess.CompletedProcess(
            args=["pg_restore"],
            returncode=1,
            stdout="",
            stderr="Invalid archive",
        )

        result = validate_backup(backup_file)

    assert result["valid"] is False
    assert result["returncode"] == 1


def test_validate_backup_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        validate_backup(tmp_path / "missing.dump")


def test_backup_database_success(tmp_path):
    def fake_run(command, **kwargs):
        if command[0] == "pg_dump":
            output_index = command.index("-f") + 1
            Path(command[output_index]).write_bytes(b"fake backup")

        return subprocess.CompletedProcess(
            args=command,
            returncode=0,
            stdout="",
            stderr="",
        )

    with patch(
        "infrapilot.postgres_backup.subprocess.run",
        side_effect=fake_run,
    ) as mock_run:

        result = backup_database(
            dbname="test_db",
            backup_dir=tmp_path,
            username="test_user",
        )

    backup_file = Path(result["backup_file"])

    assert result["success"] is True
    assert result["database"] == "test_db"
    assert result["format"] == "custom"
    assert backup_file.exists()
    assert result["size_bytes"] == len(b"fake backup")
    assert mock_run.call_count == 2
    assert not list(tmp_path.glob("*.tmp"))


def test_backup_database_dump_failure(tmp_path):
    with patch("infrapilot.postgres_backup.subprocess.run") as mock_run:
        mock_run.return_value = subprocess.CompletedProcess(
            args=["pg_dump"],
            returncode=1,
            stdout="",
            stderr="Database connection failed",
        )

        with pytest.raises(RuntimeError):
            backup_database(
                dbname="test_db",
                backup_dir=tmp_path,
            )

    assert not list(tmp_path.glob("*.tmp"))


def test_backup_database_empty_archive(tmp_path):
    def fake_run(command, **kwargs):
        if command[0] == "pg_dump":
            output_index = command.index("-f") + 1
            Path(command[output_index]).write_bytes(b"")

        return subprocess.CompletedProcess(
            args=command,
            returncode=0,
            stdout="",
            stderr="",
        )

    with patch(
        "infrapilot.postgres_backup.subprocess.run",
        side_effect=fake_run,
    ):
        with pytest.raises(RuntimeError, match="empty archive"):
            backup_database(
                dbname="test_db",
                backup_dir=tmp_path,
            )

    assert not list(tmp_path.iterdir())


def test_backup_database_timeout(tmp_path):
    with patch("infrapilot.postgres_backup.subprocess.run") as mock_run:
        mock_run.side_effect = subprocess.TimeoutExpired(
            cmd="pg_dump",
            timeout=120,
        )

        with pytest.raises(TimeoutError):
            backup_database(
                dbname="test_db",
                backup_dir=tmp_path,
            )

    assert not list(tmp_path.iterdir())


def test_restore_database_success(tmp_path):
    backup_file = tmp_path / "backup.dump"
    backup_file.write_bytes(b"fake backup")

    with patch("infrapilot.postgres_backup.subprocess.run") as mock_run:
        mock_run.return_value = subprocess.CompletedProcess(
            args=["pg_restore"],
            returncode=0,
            stdout="Restore completed",
            stderr="",
        )

        result = restore_database(
            backup_file=backup_file,
            target_db="restore_db",
            username="test_user",
        )

    command = mock_run.call_args.args[0]

    assert result["success"] is True
    assert result["target_database"] == "restore_db"
    assert "--no-owner" in command
    assert "--no-privileges" in command
    assert "--clean" not in command


def test_restore_database_failure(tmp_path):
    backup_file = tmp_path / "backup.dump"
    backup_file.write_bytes(b"fake backup")

    with patch("infrapilot.postgres_backup.subprocess.run") as mock_run:
        mock_run.return_value = subprocess.CompletedProcess(
            args=["pg_restore"],
            returncode=1,
            stdout="",
            stderr="Restore failed",
        )

        with pytest.raises(RuntimeError, match="Restore failed"):
            restore_database(
                backup_file=backup_file,
                target_db="restore_db",
            )


def test_restore_database_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        restore_database(
            backup_file=tmp_path / "missing.dump",
            target_db="restore_db",
        )


def test_restore_database_timeout(tmp_path):
    backup_file = tmp_path / "backup.dump"
    backup_file.write_bytes(b"fake backup")

    with patch("infrapilot.postgres_backup.subprocess.run") as mock_run:
        mock_run.side_effect = subprocess.TimeoutExpired(
            cmd="pg_restore",
            timeout=120,
        )

        with pytest.raises(TimeoutError):
            restore_database(
                backup_file=backup_file,
                target_db="restore_db",
            )


def test_invalid_environment():
    with pytest.raises(ValueError):
        validate_backup("backup.dump", env={"INVALID": 123})
