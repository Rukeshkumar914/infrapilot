
import pytest

from infrapilot.bash_automation import (
    validate_bash_script,
    run_bash_script,
)


def create_script(tmp_path, name, content):
    script = tmp_path / name
    script.write_text(content, encoding="utf-8")
    return script


def test_validate_valid_bash_script(tmp_path):
    script = create_script(
        tmp_path,
        "valid.sh",
        "#!/bin/bash\necho 'Hello InfraPilot'\n",
    )

    result = validate_bash_script(script)

    assert result["valid"] is True
    assert result["returncode"] == 0


def test_validate_invalid_bash_script(tmp_path):
    script = create_script(
        tmp_path,
        "invalid.sh",
        "#!/bin/bash\nif then\n",
    )

    result = validate_bash_script(script)

    assert result["valid"] is False
    assert result["returncode"] != 0
    assert result["stderr"]


def test_validate_missing_script(tmp_path):
    with pytest.raises(FileNotFoundError):
        validate_bash_script(tmp_path / "missing.sh")


def test_validate_directory_instead_of_script(tmp_path):
    with pytest.raises(ValueError):
        validate_bash_script(tmp_path)


def test_validate_invalid_timeout(tmp_path):
    script = create_script(tmp_path, "test.sh", "echo test\n")

    with pytest.raises(ValueError):
        validate_bash_script(script, timeout=0)


def test_run_bash_script_success(tmp_path):
    script = create_script(
        tmp_path,
        "success.sh",
        "#!/bin/bash\necho 'InfraPilot running'\n",
    )

    result = run_bash_script(script)

    assert result["success"] is True
    assert result["returncode"] == 0
    assert "InfraPilot running" in result["stdout"]


def test_run_bash_script_failure(tmp_path):
    script = create_script(
        tmp_path,
        "failure.sh",
        "#!/bin/bash\necho 'Something failed' >&2\nexit 1\n",
    )

    result = run_bash_script(script)

    assert result["success"] is False
    assert result["returncode"] == 1
    assert "Something failed" in result["stderr"]


def test_run_bash_script_with_arguments(tmp_path):
    script = create_script(
        tmp_path,
        "arguments.sh",
        "#!/bin/bash\necho \"$1\"\n",
    )

    result = run_bash_script(
        script,
        args=["InfraPilot"],
    )

    assert result["success"] is True
    assert "InfraPilot" in result["stdout"]


def test_run_bash_script_with_environment_variable(tmp_path):
    script = create_script(
        tmp_path,
        "environment.sh",
        "#!/bin/bash\necho \"$APP_NAME\"\n",
    )

    result = run_bash_script(
        script,
        env={"APP_NAME": "InfraPilot"},
    )

    assert result["success"] is True
    assert "InfraPilot" in result["stdout"]


def test_run_bash_script_timeout(tmp_path):
    script = create_script(
        tmp_path,
        "timeout.sh",
        "#!/bin/bash\nsleep 5\n",
    )

    with pytest.raises(TimeoutError):
        run_bash_script(script, timeout=0.2)


def test_run_bash_script_invalid_arguments(tmp_path):
    script = create_script(
        tmp_path,
        "arguments.sh",
        "#!/bin/bash\necho test\n",
    )

    with pytest.raises(ValueError):
        run_bash_script(script, args="invalid")


def test_run_bash_script_invalid_environment(tmp_path):
    script = create_script(
        tmp_path,
        "environment.sh",
        "#!/bin/bash\necho test\n",
    )

    with pytest.raises(ValueError):
        run_bash_script(script, env="invalid")
