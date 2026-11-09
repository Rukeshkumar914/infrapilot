from src.infrapilot.system_info import get_system_info


def check_system_health():
    system = get_system_info()

    checks = {
        "cpu": system["cpu_usage_percent"],
        "memory": system["memory_used_percent"],
        "disk": system["disk_used_percent"],
    }

    results = {}

    for name, usage in checks.items():
        if usage >= 90:
            status = "CRITICAL"
        elif usage >= 75:
            status = "WARNING"
        else:
            status = "HEALTHY"

        results[name] = {
            "usage_percent": usage,
            "status": status,
        }

    overall_status = "HEALTHY"

    if any(item["status"] == "CRITICAL" for item in results.values()):
        overall_status = "CRITICAL"
    elif any(item["status"] == "WARNING" for item in results.values()):
        overall_status = "WARNING"

    return {
        "overall_status": overall_status,
        "checks": results,
    }
