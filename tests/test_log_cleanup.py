
import os
from datetime import datetime, timedelta, timezone

import pytest

from infrapilot.log_manager import cleanup_old_logs


def make_old_file(path, days=40):
    path.write_text("old log data", encoding="utf-8")

    old_time = (
        datetime.now(timezone.utc) - timedelta(days=days)
    ).timestamp()

    os.utime(path, (old_time, old_time))


def test_cleanup_dry_run(tmp_path):
    old_log = tmp_path / "infrapilot.log.1"
    make_old_file(old_log)

    result = cleanup_old_logs(
        tmp_path,
        retention_days=30,
    )

    assert str(old_log) in result["deleted_or_selected"]
    assert old_log.exists()
    assert result["dry_run"] is True


def test_cleanup_deletes_old_log(tmp_path):
    old_log = tmp_path / "infrapilot.log.1"
    make_old_file(old_log)

    result = cleanup_old_logs(
        tmp_path,
        retention_days=30,
        dry_run=False,
    )

    assert not old_log.exists()
    assert result["total"] == 1


def test_cleanup_skips_active_log(tmp_path):
    active_log = tmp_path / "infrapilot.log"
    make_old_file(active_log)

    cleanup_old_logs(
        tmp_path,
        retention_days=30,
        dry_run=False,
    )

    assert active_log.exists()


def test_cleanup_keeps_recent_log(tmp_path):
    recent_log = tmp_path / "infrapilot.log.1"
    recent_log.write_text("recent log", encoding="utf-8")

    cleanup_old_logs(
        tmp_path,
        retention_days=30,
        dry_run=False,
    )

    assert recent_log.exists()


def test_cleanup_preserves_unrelated_old_files(tmp_path):
    important_file = tmp_path / "important.txt"
    make_old_file(important_file)

    cleanup_old_logs(
        tmp_path,
        retention_days=30,
        dry_run=False,
    )

    assert important_file.exists()


def test_cleanup_missing_directory(tmp_path):
    missing_dir = tmp_path / "missing"

    with pytest.raises(FileNotFoundError):
        cleanup_old_logs(missing_dir)


def test_cleanup_path_is_not_directory(tmp_path):
    file_path = tmp_path / "not_a_directory"
    file_path.write_text("test", encoding="utf-8")

    with pytest.raises(NotADirectoryError):
        cleanup_old_logs(file_path)


def test_cleanup_negative_retention_days(tmp_path):
    with pytest.raises(ValueError):
        cleanup_old_logs(
            tmp_path,
            retention_days=-1,
        )


def test_cleanup_invalid_dry_run(tmp_path):
    with pytest.raises(ValueError):
        cleanup_old_logs(
            tmp_path,
            dry_run="yes",
        )
