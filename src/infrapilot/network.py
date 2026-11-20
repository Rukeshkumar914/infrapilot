
import socket
import subprocess
import platform

import psutil


def get_local_ip():
    """Return the primary local IPv4 address."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        sock.connect(("8.8.8.8", 80))
        return sock.getsockname()[0]
    except OSError:
        return None
    finally:
        sock.close()


def get_network_interfaces():
    """Return available network interfaces and their addresses."""
    interfaces = {}

    for interface, addresses in psutil.net_if_addrs().items():
        interface_data = []

        for address in addresses:
            if address.family == socket.AF_INET:
                interface_data.append({
                    "type": "IPv4",
                    "address": address.address,
                    "netmask": address.netmask,
                    "broadcast": address.broadcast,
                })

            elif address.family == socket.AF_INET6:
                interface_data.append({
                    "type": "IPv6",
                    "address": address.address,
                    "netmask": address.netmask,
                })

        interfaces[interface] = interface_data

    return interfaces


def get_dns_records(hostname):
    """Resolve a hostname to IPv4 addresses."""
    if not hostname or not hostname.strip():
        raise ValueError("Hostname cannot be empty.")

    try:
        results = socket.getaddrinfo(
            hostname,
            None,
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
        )

        return sorted({
            result[4][0] for result in results
        })

    except socket.gaierror as error:
        raise ValueError(
            f"DNS lookup failed for {hostname}: {error}"
        ) from error


def ping_host(host, count=4):
    """Check host connectivity using the system ping command."""
    if not host or not host.strip():
        raise ValueError("Host cannot be empty.")

    if count <= 0:
        raise ValueError("Count must be greater than 0.")

    if platform.system() == "Windows":
        command = ["ping", "-n", str(count), host]
    else:
        command = ["ping", "-c", str(count), host]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=count * 3 + 5,
            check=False,
        )

        return {
            "host": host,
            "packets_requested": count,
            "return_code": result.returncode,
            "reachable": result.returncode == 0,
            "output": result.stdout.strip(),
            "error": result.stderr.strip(),
        }

    except subprocess.TimeoutExpired:
        return {
            "host": host,
            "packets_requested": count,
            "reachable": False,
            "error": "Ping command timed out.",
        }

    except FileNotFoundError:
        return {
            "host": host,
            "packets_requested": count,
            "reachable": False,
            "error": "Ping command is not installed.",
        }

