
import os
import subprocess
from pathlib import Path


def _validate_inputs(script_path, timeout):
    """Validate script path and timeout."""
    path = Path(script_path).expanduser()

    if not path.exists():
        raise FileNotFoundError(f"Bash script not found: {path}")

    if not path.is_file():
        raise ValueError(f"Not a file: {path}")

    if (
        not isinstance(timeout, (int, float))
        or isinstance(timeout, bool)
        or timeout <= 0
    ):
        raise ValueError("Timeout must be a positive number.")

    return path.resolve()


def validate_bash_script(script_path, timeout=10):
    """Check Bash script syntax without executing it."""
    path = _validate_inputs(script_path, timeout)

    try:
        result = subprocess.run(
            ["bash", "-n", str(path)],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )

    except subprocess.TimeoutExpired as exc:
        raise TimeoutError(
            f"Syntax validation timed out: {path}"
        ) from exc

    return {
        "script": str(path),
        "valid": result.returncode == 0,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def run_bash_script(
    script_path,
    args=None,
    timeout=30,
    env=None,
):
    """Execute a Bash script and capture its output."""
    path = _validate_inputs(script_path, timeout)

    if args is None:
        args = []

    if not isinstance(args, (list, tuple)):
        raise ValueError("Arguments must be a list or tuple.")

    if not all(isinstance(arg, str) for arg in args):
        raise ValueError("All script arguments must be strings.")

    if env is not None:
        if not isinstance(env, dict):
            raise ValueError("Environment must be a dictionary.")

        if not all(
            isinstance(key, str) and isinstance(value, str)
            for key, value in env.items()
        ):
            raise ValueError(
                "Environment keys and values must be strings."
            )

    script_env = os.environ.copy()

    if env:
        script_env.update(env)

    try:
        result = subprocess.run(
            ["bash", str(path), *args],
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
            cwd=path.parent,
            env=script_env,
        )

    except subprocess.TimeoutExpired as exc:
        raise TimeoutError(
            f"Bash script execution timed out: {path}"
        ) from exc

    return {
        "script": str(path),
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "success": result.returncode == 0,
    }
