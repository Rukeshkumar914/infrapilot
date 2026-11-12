import json

from infrapilot import __main__ as cli


def test_generate_report_saves_json(monkeypatch, tmp_path):
    system_info = {
        "hostname": "test-machine",
        "cpu_usage_percent": 25.0,
    }

    system_health = {
        "overall_status": "HEALTHY",
        "checks": {
            "cpu": {
                "usage_percent": 25.0,
                "status": "HEALTHY",
            }
        },
    }

    monkeypatch.setattr(
        cli, "get_system_info", lambda: system_info
    )

    monkeypatch.setattr(
        cli, "check_system_health", lambda: system_health
    )

    monkeypatch.setattr(cli, "PROJECT_ROOT", tmp_path)

    cli.generate_report()

    report_file = tmp_path / "logs" / "system_report.json"

    assert report_file.exists()

    with report_file.open("r", encoding="utf-8") as file:
        report = json.load(file)

    assert report["system_information"] == system_info
    assert report["system_health"] == system_health
