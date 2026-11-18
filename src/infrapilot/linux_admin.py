
import psutil
from datetime import datetime


def get_top_processes(limit=10):
    if limit <= 0:
        raise ValueError("Limit must be greater than 0.")

    processes = []

    for process in psutil.process_iter(
        ["pid", "name", "status", "memory_percent"]
    ):
        try:
            processes.append(process.info)
        except (
            psutil.NoSuchProcess,
            psutil.AccessDenied,
            psutil.ZombieProcess
        ):
            continue

    processes.sort(
        key=lambda process: process["memory_percent"] or 0,
        reverse=True
    )

    return processes[:limit]


def get_process_details(pid):
    try:
        process = psutil.Process(pid)

        with process.oneshot():
            details = {
                "pid": process.pid,
                "name": process.name(),
                "status": process.status(),
                "cpu_percent": process.cpu_percent(interval=0.1),
                "memory_percent": round(process.memory_percent(), 2),
                "memory_rss_mb": round(
                    process.memory_info().rss / (1024 ** 2), 2
                ),
                "executable": process.exe(),
                "created_at": datetime.fromtimestamp(
                    process.create_time()
                ).isoformat()
            }

        return details

    except psutil.NoSuchProcess:
        raise ValueError(f"Process with PID {pid} does not exist.")

    except psutil.AccessDenied:
        raise PermissionError(
            f"Permission denied while accessing PID {pid}."
        )

    except psutil.ZombieProcess:
        raise ValueError(f"Process with PID {pid} is a zombie process.")
