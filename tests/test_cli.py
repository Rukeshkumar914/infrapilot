import sys

import pytest

import infrapilot.__main__ as cli


def run_cli(monkeypatch, *args):
    monkeypatch.setattr(sys, "argv", ["infrapilot", *args])
    cli.main()


def test_pg_backup_dispatch(monkeypatch):
    calls = []
    monkeypatch.setattr(
        cli,
        "display_postgres_backup",
        lambda *args: calls.append(args),
    )

    run_cli(
        monkeypatch,
        "--pg-backup", "test_db",
        "--pg-backup-dir", "test_backups",
        "--pg-host", "127.0.0.1",
        "--pg-port", "5433",
        "--pg-user", "test_user",
        "--pg-timeout", "60",
    )

    assert calls == [
        ("test_db", "test_backups", "127.0.0.1", 5433, "test_user", 60)
    ]


def test_pg_list_backups_dispatch(monkeypatch):
    calls = []
    monkeypatch.setattr(
        cli,
        "display_postgres_backups",
        lambda *args: calls.append(args),
    )

    run_cli(
        monkeypatch,
        "--pg-list-backups",
        "--pg-backup-dir", "test_backups",
    )

    assert calls == [("test_backups",)]


def test_pg_validate_backup_dispatch(monkeypatch):
    calls = []
    monkeypatch.setattr(
        cli,
        "display_validate_postgres_backup",
        lambda *args: calls.append(args),
    )

    run_cli(
        monkeypatch,
        "--pg-validate-backup", "backup.dump",
        "--pg-timeout", "45",
    )

    assert calls == [("backup.dump", 45)]


def test_pg_restore_dispatch(monkeypatch):
    calls = []
    monkeypatch.setattr(
        cli,
        "display_postgres_restore",
        lambda *args: calls.append(args),
    )

    run_cli(
        monkeypatch,
        "--pg-restore", "backup.dump", "restore_db",
        "--pg-host", "127.0.0.1",
        "--pg-port", "5433",
        "--pg-user", "test_user",
        "--pg-timeout", "90",
    )

    assert calls == [
        ("backup.dump", "restore_db", "127.0.0.1", 5433, "test_user", 90)
    ]


@pytest.mark.parametrize("port", ["0", "65536"])
def test_invalid_pg_port(monkeypatch, port):
    monkeypatch.setattr(
        sys,
        "argv",
        ["infrapilot", "--pg-list-backups", "--pg-port", port],
    )

    with pytest.raises(SystemExit) as exc:
        cli.main()

    assert exc.value.code == 2


def test_invalid_pg_timeout(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        ["infrapilot", "--pg-list-backups", "--pg-timeout", "0"],
    )

    with pytest.raises(SystemExit) as exc:
        cli.main()

    assert exc.value.code == 2
