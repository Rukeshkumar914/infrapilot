
import argparse
import json
from pathlib import Path

from infrapilot.system_info import get_system_info
from infrapilot.health import check_system_health
from infrapilot.monitor import start_monitoring
from infrapilot.linux_admin import (
    get_top_processes,
    get_process_details,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def display_system_info():
    print("\n========== SYSTEM INFORMATION ==========\n")
    print(json.dumps(get_system_info(), indent=4))


def display_system_health():
    print("\n========== SYSTEM HEALTH ==========\n")
    print(json.dumps(check_system_health(), indent=4))


def display_processes():
    print("\n========== TOP PROCESSES ==========\n")

    processes = get_top_processes(10)

    for process in processes:
        print(
            f"PID: {process['pid']} | "
            f"Name: {process['name']} | "
            f"Status: {process['status']} | "
            f"Memory: {process['memory_percent']:.2f}%"
        )


def display_process_details(pid):
    print("\n========== PROCESS DETAILS ==========\n")

    try:
        details = get_process_details(pid)
        print(json.dumps(details, indent=4))
    except (ValueError, PermissionError) as error:
        print(f"Error: {error}")


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
        description="InfraPilot - Linux Infrastructure Toolkit"
    )

    group = parser.add_mutually_exclusive_group()

    group.add_argument("--info", action="store_true")
    group.add_argument("--health", action="store_true")
    group.add_argument("--report", action="store_true")
    group.add_argument("--monitor", action="store_true")
    group.add_argument("--processes", action="store_true")

    group.add_argument(
        "--process",
        type=int,
        metavar="PID",
        help="Display details of a specific process"
    )

    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Monitoring interval in seconds"
    )

    args = parser.parse_args()

    if args.info:
        display_system_info()
    elif args.health:
        display_system_health()
    elif args.report:
        generate_report()
    elif args.monitor:
        start_monitoring(interval=args.interval)
    elif args.processes:
        display_processes()
    elif args.process is not None:
        display_process_details(args.process)
    else:
        display_system_info()
        display_system_health()


if __name__ == "__main__":
    main()
