 
from src.infrapilot.system_info import get_system_info
from infrapilot.logger import setup_logger


def check_system_health():
    logger = setup_logger()

    system = get_system_info()

    checks = {
        "cpu": system["cpu_usage_percent"],
        "memory": system["memory_used_percent"],
        "disk": system["disk_used_percent"],
    }

    results = {}

    # Check individual system components
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

        # Log individual component status
        logger.info(
            "%s usage: %.2f%% | Status: %s",
            name,
            usage,
            status
        )

    # Calculate overall system health
    overall_status = "HEALTHY"

    if any(
        item["status"] == "CRITICAL"
        for item in results.values()
    ):
        overall_status = "CRITICAL"

    elif any(
        item["status"] == "WARNING"
        for item in results.values()
    ):
        overall_status = "WARNING"

    # Log overall health status
    logger.info(
        "Overall system health: %s",
        overall_status
    )

    return {
        "overall_status": overall_status,
        "checks": results,
    }

