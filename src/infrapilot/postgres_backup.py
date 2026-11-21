
import re
import subprocess
from datetime import datetime
from pathlib import Path

from infrapilot.logger import setup_logger


logger = setup_logger()


def _validate_connection(dbname, host, port, username, timeout):
    """Validate PostgreSQL connection parameters."""

    if not isinstance(dbname, str) or not re.fullmatch(
        r"[A-Za-z0-9_]+", dbname
    ):
        raise ValueError("Invalid database name.")

    if not isinstance(host, str) or not host.strip():
        raise ValueError("Host must be a non-empty string.")

    if (
        not isinstance(port, int)
        or isinstance(port, bool)
        or not 1 <= port <= 65535
    ):
        raise ValueError("Port must be between 1 and 65535.")

    if username is not None and (
        not isinstance(username, str) or not username.strip()
    ):
        raise ValueError("Username must be a non-empty string.")

    if (
        not isinstance(timeout, (int, float))
        or isinstance(timeout, bool)
        or timeout <= 0
    ):
        raise ValueError("Timeout must be a positive number.")


def _validate_env(env):
    """Validate optional subprocess environment variables."""

    if env is None:
        return

    if not isinstance(env, dict) or not all(
        isinstance(key, str) and isinstance(value, str)
        for key, value in env.items()
    ):
        raise ValueError("Environment must contain string keys and values.")


def _connection_args(host, port, username):
    """Build PostgreSQL connection arguments."""

    args = ["-h", host, "-p", str(port)]

    if username:
        args.extend(["-U", username])

    return args


def backup_database(
    dbname,
    backup_dir="backups",
    host="localhost",
    port=5432,
    username=None,
    timeout=120,
    env=None,
):
    """Create a timestamped PostgreSQL custom-format backup."""

    _validate_connection(dbname, host, port, username, timeout)
    _validate_env(env)

    backup_path = Path(backup_dir).expanduser()
    backup_path.mkdir(parents=True, exist_ok=True)

    if not backup_path.is_dir():
        raise ValueError("Backup destination must be a directory.")

    timestamp = datetime.now().astimezone().strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    final_file = backup_path / f"{dbname}_{timestamp}.dump"
    temporary_file = backup_path / f".{dbname}_{timestamp}.tmp"

    command = [
        "pg_dump",
        *_connection_args(host, port, username),
        "-d", dbname,
        "-F", "c",
        "-f", str(temporary_file),
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
            env=env,
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"PostgreSQL backup failed: {result.stderr.strip()}"
            )

        if (
            not temporary_file.is_file()
            or temporary_file.stat().st_size == 0
        ):
            raise RuntimeError("Backup command produced an empty archive.")

        validation = subprocess.run(
            ["pg_restore", "--list", str(temporary_file)],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
            env=env,
        )

        if validation.returncode != 0:
            raise RuntimeError(
                "Backup archive validation failed: "
                f"{validation.stderr.strip()}"
            )

        temporary_file.replace(final_file)

        logger.info("PostgreSQL backup created: %s", final_file)

        return {
            "success": True,
            "database": dbname,
            "backup_file": str(final_file),
            "size_bytes": final_file.stat().st_size,
            "format": "custom",
        }

    except subprocess.TimeoutExpired as exc:
        raise TimeoutError(
            "PostgreSQL backup operation timed out."
        ) from exc

    finally:
        temporary_file.unlink(missing_ok=True)


def list_backups(backup_dir="backups"):
    """List PostgreSQL dump files in a backup directory."""

    directory = Path(backup_dir).expanduser()

    if not directory.exists():
        raise FileNotFoundError(
            f"Backup directory not found: {directory}"
        )

    if not directory.is_dir():
        raise ValueError("Backup path must be a directory.")

    backups = []

    for file_path in sorted(directory.glob("*.dump")):
        if file_path.is_file():
            backups.append({
                "filename": file_path.name,
                "path": str(file_path.resolve()),
                "size_bytes": file_path.stat().st_size,
            })

    return backups


def validate_backup(backup_file, timeout=30, env=None):
    """Check whether a custom-format archive can be listed."""

    if (
        not isinstance(timeout, (int, float))
        or isinstance(timeout, bool)
        or timeout <= 0
    ):
        raise ValueError("Timeout must be a positive number.")

    _validate_env(env)

    path = Path(backup_file).expanduser().resolve()

    if not path.exists():
        raise FileNotFoundError(f"Backup file not found: {path}")

    if not path.is_file():
        raise ValueError("Backup path must be a file.")

    try:
        result = subprocess.run(
            ["pg_restore", "--list", str(path)],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
            env=env,
        )

    except subprocess.TimeoutExpired as exc:
        raise TimeoutError(
            "Backup validation timed out."
        ) from exc

    return {
        "valid": result.returncode == 0,
        "backup_file": str(path),
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def restore_database(
    backup_file,
    target_db,
    host="localhost",
    port=5432,
    username=None,
    timeout=120,
    env=None,
):
    """Restore a custom-format backup into an existing database."""

    _validate_connection(target_db, host, port, username, timeout)
    _validate_env(env)

    path = Path(backup_file).expanduser().resolve()

    if not path.exists():
        raise FileNotFoundError(
            f"Backup file not found: {path}"
        )

    if not path.is_file():
        raise ValueError("Backup path must be a file.")

    command = [
        "pg_restore",
        *_connection_args(host, port, username),
        "-d", target_db,
        "--no-owner",
        "--no-privileges",
        str(path),
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
            env=env,
        )

    except subprocess.TimeoutExpired as exc:
        raise TimeoutError(
            "PostgreSQL restore operation timed out."
        ) from exc

    if result.returncode != 0:
        raise RuntimeError(
            f"PostgreSQL restore failed: {result.stderr.strip()}"
        )

    logger.info(
        "PostgreSQL backup restored into database: %s",
        target_db,
    )

    return {
        "success": True,
        "backup_file": str(path),
        "target_database": target_db,
        "stdout": result.stdout,
    }
