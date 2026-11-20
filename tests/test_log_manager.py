import pytest

from infrapilot.log_manager import (
    read_logs,
    analyze_logs,
    filter_logs,
)


@pytest.fixture
def sample_log_file(tmp_path):
    log_file = tmp_path / "infrapilot.log"

    log_file.write_text(
        "2026-11-20 10:00:00 | INFO | Application started\n"
        "2026-11-20 10:01:00 | WARNING | High memory usage\n"
        "2026-11-20 10:02:00 | ERROR | Connection failed\n"
        "2026-11-20 10:03:00 | CRITICAL | System failure\n"
        "2026-11-20 10:04:00 | INFO | Application running\n",
        encoding="utf-8",
    )

    return log_file


def test_read_logs(sample_log_file):
    logs = read_logs(sample_log_file)

    assert len(logs) == 5
    assert "Application started" in logs[0]


def test_read_logs_with_limit(sample_log_file):
    logs = read_logs(sample_log_file, limit=2)

    assert len(logs) == 2
    assert "Application running" in logs[-1]


def test_read_logs_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        read_logs(tmp_path / "missing.log")


def test_read_logs_invalid_limit(sample_log_file):
    with pytest.raises(ValueError):
        read_logs(sample_log_file, limit=0)


def test_analyze_logs(sample_log_file):
    result = analyze_logs(sample_log_file)

    assert result["total_entries"] == 5
    assert result["severity_counts"]["INFO"] == 2
    assert result["severity_counts"]["WARNING"] == 1
    assert result["severity_counts"]["ERROR"] == 1
    assert result["severity_counts"]["CRITICAL"] == 1


def test_filter_error_logs(sample_log_file):
    logs = filter_logs(sample_log_file, "ERROR")

    assert len(logs) == 1
    assert "Connection failed" in logs[0]


def test_filter_logs_case_insensitive(sample_log_file):
    logs = filter_logs(sample_log_file, "warning")

    assert len(logs) == 1
    assert "High memory usage" in logs[0]


def test_filter_invalid_level(sample_log_file):
    with pytest.raises(ValueError):
        filter_logs(sample_log_file, "DEBUG")
