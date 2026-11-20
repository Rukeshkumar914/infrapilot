import socket
import subprocess
from unittest.mock import Mock, patch

import psutil
import pytest

from infrapilot.network import (
    get_local_ip,
    get_network_interfaces,
    get_dns_records,
    ping_host,
)


# Test local IP
@patch("infrapilot.network.socket.socket")
def test_get_local_ip(mock_socket):
    mock_sock = mock_socket.return_value
    mock_sock.getsockname.return_value = ("192.168.1.10", 0)

    assert get_local_ip() == "192.168.1.10"
    mock_sock.close.assert_called_once()


@patch("infrapilot.network.socket.socket")
def test_get_local_ip_failure(mock_socket):
    mock_sock = mock_socket.return_value
    mock_sock.connect.side_effect = OSError("Network error")

    assert get_local_ip() is None
    mock_sock.close.assert_called_once()


# Test network interfaces
@patch("infrapilot.network.psutil.net_if_addrs")
def test_get_network_interfaces(mock_interfaces):
    ipv4 = Mock()
    ipv4.family = socket.AF_INET
    ipv4.address = "192.168.1.10"
    ipv4.netmask = "255.255.255.0"
    ipv4.broadcast = "192.168.1.255"

    mock_interfaces.return_value = {
        "wlan0": [ipv4]
    }

    result = get_network_interfaces()

    assert "wlan0" in result
    assert result["wlan0"][0]["type"] == "IPv4"
    assert result["wlan0"][0]["address"] == "192.168.1.10"


# Test DNS
@patch("infrapilot.network.socket.getaddrinfo")
def test_get_dns_records(mock_dns):
    mock_dns.return_value = [
        (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("8.8.8.8", 0)),
        (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("1.1.1.1", 0)),
    ]

    result = get_dns_records("example.com")

    assert result == ["1.1.1.1", "8.8.8.8"]


def test_get_dns_records_empty_hostname():
    with pytest.raises(ValueError):
        get_dns_records("")


@patch("infrapilot.network.socket.getaddrinfo")
def test_get_dns_records_failure(mock_dns):
    mock_dns.side_effect = socket.gaierror("DNS error")

    with pytest.raises(ValueError, match="DNS lookup failed"):
        get_dns_records("invalid.example")


# Test ping
@patch("infrapilot.network.subprocess.run")
def test_ping_host_success(mock_run):
    mock_run.return_value = Mock(
        returncode=0,
        stdout="4 packets transmitted, 4 received",
        stderr="",
    )

    result = ping_host("google.com", count=4)

    assert result["reachable"] is True
    assert result["packets_requested"] == 4
    assert result["return_code"] == 0


@patch("infrapilot.network.subprocess.run")
def test_ping_host_failure(mock_run):
    mock_run.return_value = Mock(
        returncode=1,
        stdout="100% packet loss",
        stderr="",
    )

    result = ping_host("unreachable.example")

    assert result["reachable"] is False


def test_ping_host_empty():
    with pytest.raises(ValueError):
        ping_host("")


def test_ping_host_invalid_count():
    with pytest.raises(ValueError):
        ping_host("google.com", count=0)


@patch("infrapilot.network.subprocess.run")
def test_ping_host_timeout(mock_run):
    mock_run.side_effect = subprocess.TimeoutExpired(
        cmd="ping",
        timeout=10,
    )

    result = ping_host("google.com")

    assert result["reachable"] is False
    assert result["error"] == "Ping command timed out."


@patch("infrapilot.network.subprocess.run")
def test_ping_host_command_missing(mock_run):
    mock_run.side_effect = FileNotFoundError

    result = ping_host("google.com")

    assert result["reachable"] is False
    assert result["error"] == "Ping command is not installed."
