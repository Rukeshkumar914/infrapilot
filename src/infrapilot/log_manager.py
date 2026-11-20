
from pathlib import Path
from collections import Counter
from datetime import datetime, timedelta, timezone


def read_logs(log_file, limit=None):
    """Read log entries from a log file."""
    path = Path(log_file).expanduser()

    if not path.exists():
        raise FileNotFoundError(f"Log file not found: {path}")

    if not path.is_file():
        raise ValueError(f"Not a file: {path}")

    if limit is not None and (
        not isinstance(limit, int)
        or isinstance(limit, bool)
        or limit <= 0
    ):
        raise ValueError("Limit must be a positive integer.")

    with path.open("r", encoding="utf-8") as file:
        lines = file.readlines()

    if limit is not None:
        lines = lines[-limit:]

    return [line.rstrip("\n") for line in lines]


def analyze_logs(log_file):
    """Count log entries by severity."""
    lines = read_logs(log_file)

    counts = Counter({
        "INFO": 0,
        "WARNING": 0,
        "ERROR": 0,
        "CRITICAL": 0,
    })

    for line in lines:
        parts = line.split("|")

        if len(parts) < 3:
            continue

        level = parts[1].strip().upper()

        if level in counts:
            counts[level] += 1

    return {
        "total_entries": sum(counts.values()),
        "severity_counts": dict(counts),
    }


def filter_logs(log_file, level):
    """Return log entries matching a severity level."""
    valid_levels = {"INFO", "WARNING", "ERROR", "CRITICAL"}
    level = level.upper()

    if level not in valid_levels:
        raise ValueError(f"Invalid log level: {level}")

    lines = read_logs(log_file)
    filtered = []

    for line in lines:
        parts = line.split("|")

        if len(parts) >= 3:
            if parts[1].strip().upper() == level:
                filtered.append(line)

    return filtered


def cleanup_old_logs(
    log_dir,
    retention_days=30,
    dry_run=True,
    active_log="infrapilot.log",
):
    """Safely identify or delete expired rotated log files."""
    directory = Path(log_dir).expanduser()

    if not directory.exists():
        raise FileNotFoundError(
            f"Log directory not found: {directory}"
        )

    if not directory.is_dir():
        raise NotADirectoryError(
            f"Not a directory: {directory}"
        )

    if (
        not isinstance(retention_days, int)
        or isinstance(retention_days, bool)
        or retention_days < 0
    ):
        raise ValueError(
            "Retention days must be a non-negative integer."
        )

    if not isinstance(dry_run, bool):
        raise ValueError("dry_run must be True or False.")

    active_name = Path(active_log).name
    rotated_prefix = f"{active_name}."

    cutoff = datetime.now(timezone.utc) - timedelta(
        days=retention_days
    )

    selected = []
    skipped = []

    for file_path in directory.iterdir():
        if not file_path.is_file():
            continue

        # Never delete the active log.
        if file_path.name == active_name:
            skipped.append(str(file_path))
            continue

        # Only process rotated files of the active log.
        if not file_path.name.startswith(rotated_prefix):
            continue

        modified_time = datetime.fromtimestamp(
            file_path.stat().st_mtime,
            tz=timezone.utc,
        )

        if modified_time < cutoff:
            selected.append(str(file_path))

            if not dry_run:
                file_path.unlink()

    return {
        "directory": str(directory.resolve()),
        "retention_days": retention_days,
        "dry_run": dry_run,
        "deleted_or_selected": selected,
        "skipped": skipped,
        "total": len(selected),
    }
