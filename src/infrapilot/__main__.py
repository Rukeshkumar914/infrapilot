
import argparse
import re
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
from infrapilot.bash_automation import (
    validate_bash_script,
    run_bash_script,
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


def display_validate_bash(script, timeout):
    print("\n========== BASH SCRIPT VALIDATION ==========\n")

    try:
        result = validate_bash_script(
            script,
            timeout=timeout,
        )
        print(json.dumps(result, indent=4))

    except (OSError, ValueError, TimeoutError) as error:
        print(f"Error: {error}")


def display_run_bash(script, script_args, timeout, environment):
    print("\n========== BASH SCRIPT EXECUTION ==========\n")
    print("Warning: Only execute trusted scripts.\n")

    try:
        result = run_bash_script(
            script,
            args=script_args,
            timeout=timeout,
            env=environment,
        )
        print(json.dumps(result, indent=4))

    except (OSError, ValueError, TimeoutError) as error:
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

    group.add_argument(
        "--validate-bash",
        metavar="SCRIPT",
        help="Validate Bash script syntax without execution",
    )

    group.add_argument(
        "--run-bash",
        metavar="SCRIPT",
        help="Execute a trusted Bash script",
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

    parser.add_argument(
        "--bash-timeout",
        type=int,
        default=30,
        help="Bash script timeout in seconds (default: 30)",
    )

    parser.add_argument(
        "--bash-arg",
        action="append",
        default=[],
        help="Argument to pass to Bash script; repeat for multiple arguments",
    )

    parser.add_argument(
        "--bash-env",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Environment variable for Bash script; repeat for multiple variables",
    )

    args = parser.parse_args()

    if args.count <= 0:
        parser.error("--count must be greater than 0")

    if args.interval <= 0:
        parser.error("--interval must be greater than 0")

    if args.bash_timeout <= 0:
        parser.error("--bash-timeout must be greater than 0")

    if args.overwrite and not (args.create_file or args.move):
        parser.error("--overwrite requires --create-file or --move")

    if (args.bash_arg or args.bash_env) and not args.run_bash:
        parser.error("--bash-arg and --bash-env require --run-bash")

    if args.bash_timeout != 30 and not (
        args.run_bash or args.validate_bash
    ):
        parser.error(
            "--bash-timeout requires --run-bash or --validate-bash"
        )

    environment = {}

    for item in args.bash_env:
        if "=" not in item:
            parser.error(
                f"Invalid --bash-env format: {item}. Use KEY=VALUE."
            )

        key, value = item.split("=", 1)

        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key):
            parser.error(f"Invalid environment variable name: {key}")

        environment[key] = value

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

    elif args.validate_bash:
        display_validate_bash(
            args.validate_bash,
            args.bash_timeout,
        )

    elif args.run_bash:
        display_run_bash(
            args.run_bash,
            args.bash_arg,
            args.bash_timeout,
            environment,
        )

    else:
        display_system_info()
        display_system_health()


if __name__ == "__main__":
    main()
