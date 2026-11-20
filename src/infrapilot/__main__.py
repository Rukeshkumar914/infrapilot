
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
from infrapilot.network import (
    get_local_ip,
    get_network_interfaces,
    get_dns_records,
    ping_host,
)
from infrapilot.automation import (
    create_directory,
    create_file,
    list_directory,
    move_path,
    get_path_info,
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
        memory = process["memory_percent"] or 0
        print(
            f"PID: {process['pid']} | "
            f"Name: {process['name']} | "
            f"Status: {process['status']} | "
            f"Memory: {memory:.2f}%"
        )


def display_process_details(pid):
    print("\n========== PROCESS DETAILS ==========\n")

    try:
        print(json.dumps(get_process_details(pid), indent=4))
    except (ValueError, PermissionError) as error:
        print(f"Error: {error}")


def display_network():
    print("\n========== NETWORK INFORMATION ==========\n")

    network_info = {
        "local_ip": get_local_ip(),
        "interfaces": get_network_interfaces(),
    }

    print(json.dumps(network_info, indent=4))


def display_dns(hostname):
    print("\n========== DNS LOOKUP ==========\n")

    try:
        result = {
            "hostname": hostname,
            "ipv4_addresses": get_dns_records(hostname),
        }
        print(json.dumps(result, indent=4))
    except ValueError as error:
        print(f"Error: {error}")


def display_ping(host, count):
    print("\n========== NETWORK CONNECTIVITY ==========\n")

    result = ping_host(host, count=count)
    print(json.dumps(result, indent=4))


def display_create_directory(path):
    print("\n========== CREATE DIRECTORY ==========\n")

    try:
        result = create_directory(path)
        print(json.dumps(result, indent=4))
    except OSError as error:
        print(f"Error: {error}")


def display_create_file(path, content, overwrite):
    print("\n========== CREATE FILE ==========\n")

    try:
        result = create_file(
            path,
            content=content,
            overwrite=overwrite,
        )
        print(json.dumps(result, indent=4))
    except OSError as error:
        print(f"Error: {error}")


def display_list_directory(path):
    print("\n========== DIRECTORY CONTENTS ==========\n")

    try:
        result = list_directory(path)
        print(json.dumps(result, indent=4))
    except OSError as error:
        print(f"Error: {error}")


def display_move(source, destination, overwrite):
    print("\n========== MOVE FILE OR DIRECTORY ==========\n")

    try:
        result = move_path(
            source,
            destination,
            overwrite=overwrite,
        )
        print(json.dumps(result, indent=4))
    except OSError as error:
        print(f"Error: {error}")


def display_path_info(path):
    print("\n========== PATH INFORMATION ==========\n")

    try:
        result = get_path_info(path)
        print(json.dumps(result, indent=4))
    except OSError as error:
        print(f"Error: {error}")


def generate_report():
    print("\n========== GENERATING SYSTEM REPORT ==========\n")

    report = {
        "system_information": get_system_info(),
        "system_health": check_system_health(),
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
        description="InfraPilot - Linux Infrastructure Toolkit",
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
        help="Display details of a specific process",
    )

    group.add_argument(
        "--network",
        action="store_true",
        help="Display local IP and network interfaces",
    )

    group.add_argument(
        "--dns",
        metavar="HOSTNAME",
        help="Resolve hostname using DNS",
    )

    group.add_argument(
        "--ping",
        metavar="HOST",
        help="Check network connectivity to a host",
    )

    group.add_argument(
        "--create-dir",
        metavar="PATH",
        help="Create a directory",
    )

    group.add_argument(
        "--create-file",
        metavar="PATH",
        help="Create a file",
    )

    group.add_argument(
        "--list-dir",
        metavar="PATH",
        help="List directory contents",
    )

    group.add_argument(
        "--move",
        nargs=2,
        metavar=("SOURCE", "DESTINATION"),
        help="Move a file or directory",
    )

    group.add_argument(
        "--path-info",
        metavar="PATH",
        help="Display file or directory information",
    )

    parser.add_argument(
        "--content",
        default="",
        help="Content to write into a new file",
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow overwriting existing destination",
    )

    parser.add_argument(
        "--count",
        type=int,
        default=4,
        help="Number of ping packets (default: 4)",
    )

    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Monitoring interval in seconds",
    )

    args = parser.parse_args()

    if args.count <= 0:
        parser.error("--count must be greater than 0")

    if args.interval <= 0:
        parser.error("--interval must be greater than 0")

    if args.overwrite and not (args.create_file or args.move):
        parser.error("--overwrite requires --create-file or --move")

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

    elif args.network:
        display_network()

    elif args.dns:
        display_dns(args.dns)

    elif args.ping:
        display_ping(args.ping, args.count)

    elif args.create_dir:
        display_create_directory(args.create_dir)

    elif args.create_file:
        display_create_file(
            args.create_file,
            args.content,
            args.overwrite,
        )

    elif args.list_dir:
        display_list_directory(args.list_dir)

    elif args.move:
        display_move(
            args.move[0],
            args.move[1],
            args.overwrite,
        )

    elif args.path_info:
        display_path_info(args.path_info)

    else:
        display_system_info()
        display_system_health()


if __name__ == "__main__":
    main()
