
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import psutil
import pytest

from infrapilot.linux_admin import (
    get_top_processes,
    get_process_details,
)


def test_get_top_processes_sorts_by_memory():
    processes = [
        SimpleNamespace(info={
            "pid": 101,
            "name": "process-a",
            "status": "sleeping",
            "memory_percent": 5.0,
        }),
        SimpleNamespace(info={
            "pid": 102,
            "name": "process-b",
            "status": "running",
            "memory_percent": 15.0,
        }),
        SimpleNamespace(info={
            "pid": 103,
            "name": "process-c",
            "status": "sleeping",
            "memory_percent": 10.0,
        }),
    ]

    with patch(
        "infrapilot.linux_admin.psutil.process_iter",
        return_value=processes,
    ):
        result = get_top_processes(3)

    assert [process["pid"] for process in result] == [102, 103, 101]


def test_get_top_processes_respects_limit():
    processes = [
        SimpleNamespace(info={
            "pid": pid,
            "name": f"process-{pid}",
            "status": "sleeping",
            "memory_percent": float(pid),
        })
        for pid in range(1, 6)
    ]

    with patch(
        "infrapilot.linux_admin.psutil.process_iter",
        return_value=processes,
    ):
        result = get_top_processes(2)

    assert len(result) == 2


def test_get_top_processes_rejects_invalid_limit():
    with pytest.raises(ValueError):
        get_top_processes(0)


def test_get_process_details_returns_process_information():
    process = MagicMock()
    process.pid = 1234
    process.name.return_value = "test-process"
    process.status.return_value = "running"
    process.cpu_percent.return_value = 2.5
    process.memory_percent.return_value = 1.5
    process.memory_info.return_value = SimpleNamespace(
        rss=10 * 1024 * 1024
    )
    process.exe.return_value = "/usr/bin/test-process"
    process.create_time.return_value = 1700000000

    with patch(
        "infrapilot.linux_admin.psutil.Process",
        return_value=process,
    ):
        result = get_process_details(1234)

    assert result["pid"] == 1234
    assert result["name"] == "test-process"
    assert result["status"] == "running"
    assert result["cpu_percent"] == 2.5
    assert result["memory_percent"] == 1.5
    assert result["memory_rss_mb"] == 10.0
    assert result["executable"] == "/usr/bin/test-process"
    assert "created_at" in result


def test_get_process_details_handles_missing_process():
    with patch(
        "infrapilot.linux_admin.psutil.Process",
        side_effect=psutil.NoSuchProcess(999999),
    ):
        with pytest.raises(ValueError, match="does not exist"):
            get_process_details(999999)


def test_get_process_details_handles_access_denied():
    with patch(
        "infrapilot.linux_admin.psutil.Process",
        side_effect=psutil.AccessDenied(1234),
    ):
        with pytest.raises(PermissionError, match="Permission denied"):
            get_process_details(1234)


def test_get_process_details_handles_zombie_process():
    with patch(
        "infrapilot.linux_admin.psutil.Process",
        side_effect=psutil.ZombieProcess(1234),
    ):
        with pytest.raises(ValueError, match="zombie process"):
            get_process_details(1234)
