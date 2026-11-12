import argparse
import json
from pathlib import Path

from infrapilot.system_info import get_system_info
from infrapilot.health import check_system_health


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def display_system_info():
    print("\n========== SYSTEM INFORMATION ==========\n")

    system_info = get_system_info()
    print(json.dumps(system_info, indent=4))


def display_system_health():
    print("\n========== SYSTEM HEALTH ==========\n")

    health = check_system_health()
    print(json.dumps(health, indent=4))


def generate_report():
    print("\n========== GENERATING SYSTEM REPORT ==========\n")

    report = {
        "system_information": get_system_info(),
        "system_health": check_system_health()
    }

    log_dir = PROJECT_ROOT / "logs"
    log_dir.mkdir(exist_ok=True)

    report_file = log_dir / "system_report.json"

    with report_file.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=4)

    print(f"Report successfully saved to: {report_file}")


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

    group.add_argument(
        "--report",
        action="store_true",
        help="Generate and save JSON system report"
    )

    args = parser.parse_args()

    if args.info:
        display_system_info()

    elif args.health:
        display_system_health()

    elif args.report:
        generate_report()

    else:
        display_system_info()
        display_system_health()


if __name__ == "__main__":
    main()
