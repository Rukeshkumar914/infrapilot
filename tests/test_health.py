from src.infrapilot.health import check_system_health


def test_healthy_system(monkeypatch):
    monkeypatch.setattr(
        "src.infrapilot.health.get_system_info",
        lambda: {
            "cpu_usage_percent": 30,
            "memory_used_percent": 40,
            "disk_used_percent": 50,
        },
    )

    result = check_system_health()

    assert result["overall_status"] == "HEALTHY"


def test_warning_system(monkeypatch):
    monkeypatch.setattr(
        "src.infrapilot.health.get_system_info",
        lambda: {
            "cpu_usage_percent": 80,
            "memory_used_percent": 40,
            "disk_used_percent": 50,
        },
    )

    result = check_system_health()

    assert result["overall_status"] == "WARNING"


def test_critical_system(monkeypatch):
    monkeypatch.setattr(
        "src.infrapilot.health.get_system_info",
        lambda: {
            "cpu_usage_percent": 95,
            "memory_used_percent": 40,
            "disk_used_percent": 50,
        },
    )

    result = check_system_health()

    assert result["overall_status"] == "CRITICAL"
