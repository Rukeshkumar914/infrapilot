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
        "cpu_physical_cores",
        "cpu_logical_cores",
        "cpu_usage_percent",
        "memory_total_gb",
        "memory_used_gb",
        "memory_available_gb",
        "memory_used_percent",
        "disk_total_gb",
        "disk_used_gb",
        "disk_free_gb",
        "disk_used_percent",
        "checked_at",
    ]

    for field in required_fields:
        assert field in result


def test_system_metrics_are_valid():
    result = get_system_info()

    assert result["cpu_physical_cores"] > 0
    assert result["cpu_logical_cores"] > 0

    assert result["memory_total_gb"] > 0
    assert result["memory_used_gb"] >= 0
    assert result["memory_available_gb"] >= 0

    assert result["disk_total_gb"] > 0
    assert result["disk_used_gb"] >= 0
    assert result["disk_free_gb"] >= 0

    assert 0 <= result["cpu_usage_percent"] <= 100
    assert 0 <= result["memory_used_percent"] <= 100
    assert 0 <= result["disk_used_percent"] <= 100
