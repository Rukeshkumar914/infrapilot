import argparse
import json

from infrapilot.system_info import get_system_info
from infrapilot.health import check_system_health


def display_system_info():
    print("\n========== SYSTEM INFORMATION ==========\n")

    system_info = get_system_info()
    print(json.dumps(system_info, indent=4))


def display_system_health():
    print("\n========== SYSTEM HEALTH ==========\n")

    health = check_system_health()
    print(json.dumps(health, indent=4))


def main():
    parser = argparse.ArgumentParser(
        prog="infrapilot",
        description="InfraPilot - Linux System Monitoring Tool"
    )

    group = parser.add_mutually_exclusive_group()

    group.add_argument(
        "--info",
        action="store_true",
        help="Display system information"
    )

    group.add_argument(
        "--health",
        action="store_true",
        help="Display system health"
    )

    args = parser.parse_args()

    if args.info:
        display_system_info()

    elif args.health:
        display_system_health()

    else:
        display_system_info()
        display_system_health()


if __name__ == "__main__":
    main()
