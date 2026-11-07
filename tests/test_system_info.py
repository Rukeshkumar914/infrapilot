from src.infrapilot.system_info import get_system_info


def test_get_system_info_returns_dictionary():
    result = get_system_info()
    assert isinstance(result, dict)


def test_system_info_contains_required_fields():
    result = get_system_info()

    required_fields = [
        "hostname",
        "operating_system",
        "os_release",
        "python_version",
        "cpu_count",
        "cpu_usage_percent",
        "memory_total_gb",
        "memory_used_percent",
        "disk_total_gb",
        "disk_used_percent",
        "checked_at",
    ]

    for field in required_fields:
        assert field in result


def test_system_metrics_are_valid():
    result = get_system_info()

    assert result["cpu_count"] > 0
    assert result["memory_total_gb"] > 0
    assert result["disk_total_gb"] > 0
    assert 0 <= result["cpu_usage_percent"] <= 100
    assert 0 <= result["memory_used_percent"] <= 100
    assert 0 <= result["disk_used_percent"] <= 100
