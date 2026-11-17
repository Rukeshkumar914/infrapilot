import time

from infrapilot.health import check_system_health
from infrapilot.logger import setup_logger


def start_monitoring(interval=60):
    if interval <= 0:
        raise ValueError(
            "Monitoring interval must be greater than 0 seconds."
        )
    logger = setup_logger()

    logger.info("InfraPilot continuous monitoring started")
    logger.info("Monitoring interval: %s seconds", interval)

    try:
        while True:
            print("\n========== SYSTEM MONITORING ==========\n")

            health = check_system_health()

            print(f"Overall Status: {health['overall_status']}")

            for name, details in health["checks"].items():
                print(
                    f"{name.upper()}: "
                    f"{details['usage_percent']}% "
                    f"| {details['status']}"
                )

            print(f"\nNext check in {interval} seconds...")

            time.sleep(interval)

    except KeyboardInterrupt:
        logger.info("InfraPilot monitoring stopped by user")
        print("\nMonitoring stopped safely.")


if __name__ == "__main__":
    start_monitoring()
