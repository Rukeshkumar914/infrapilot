# InfraPilot

**InfraPilot** is a Python-based Linux infrastructure automation and diagnostics toolkit. It brings together system monitoring, Linux administration, network diagnostics, file automation, log management, Bash script execution, and PostgreSQL backup and restore operations through a unified command-line interface.

The project is designed to simplify common infrastructure administration tasks while providing reliable error handling, logging, and automated testing.

## Features

### 1. System Monitoring
- Collect hostname, operating system, Python version, CPU, memory, and disk information.
- Monitor CPU, RAM, and disk utilization.
- Evaluate system health using configurable status classifications.
- Generate JSON system reports.
- Support continuous monitoring with a configurable interval.

### 2. Linux Administration
- List top processes based on memory usage.
- Retrieve process details using PID.
- Handle missing, inaccessible, and zombie processes.

### 3. Network Diagnostics
- Detect the local IP address.
- Retrieve network interface information.
- Perform DNS lookups.
- Ping remote hosts and inspect command results.
- Handle network errors and timeouts.

### 4. File and Directory Automation
- Create directories and files.
- List directory contents.
- Retrieve file and directory information.
- Move files and directories.
- Protect existing files from accidental overwriting by default.

### 5. Log Management
- Read and filter log files.
- Analyze INFO, WARNING, ERROR, and CRITICAL entries.
- Clean up old rotated log files.
- Support dry-run cleanup before deleting eligible logs.
- Preserve the active log file.

### 6. Bash Automation
- Validate Bash scripts using `bash -n`.
- Execute trusted Bash scripts through Python subprocesses.
- Pass command-line arguments and environment variables.
- Capture standard output and error.
- Handle execution timeouts.

**Security note:** Bash scripts can execute arbitrary system commands. Run only scripts you trust.

### 7. PostgreSQL Backup and Restore
- Create PostgreSQL custom-format backups using `pg_dump`.
- List available backup archives.
- Validate backup archives using `pg_restore`.
- Restore backups into an existing target database.
- Handle database command failures and timeouts.

**Important:** Restore does not automatically drop or recreate the target database. Use a suitable empty target database when restoring an archive containing existing objects.

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core application |
| psutil | System resource monitoring |
| Linux | Operating environment |
| Bash | Shell automation |
| PostgreSQL | Database backup and restore |
| pg_dump / pg_restore | PostgreSQL backup utilities |
| Pytest | Automated testing |
| Git & GitHub | Version control |

## Project Structure

```text
infrapilot/
├── backups/
├── logs/
├── examples/
│   └── bash_environment_demo.sh
├── src/
│   └── infrapilot/
│       ├── __init__.py
│       ├── __main__.py
│       ├── automation.py
│       ├── bash_automation.py
│       ├── health.py
│       ├── linux_admin.py
│       ├── log_manager.py
│       ├── logger.py
│       ├── monitor.py
│       ├── network.py
│       ├── postgres_backup.py
│       └── system_info.py
├── tests/
│   ├── test_automation.py
│   ├── test_bash_automation.py
│   ├── test_cli.py
│   ├── test_health.py
│   ├── test_linux_admin.py
│   ├── test_log_cleanup.py
│   ├── test_log_manager.py
│   ├── test_logger.py
│   ├── test_network.py
│   ├── test_postgres_backup.py
│   ├── test_report.py
│   └── test_system_info.py
├── pyproject.toml
├── .gitignore
└── README.md
```

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Rukeshkumar914/infrapilot.git
cd infrapilot
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the environment on Linux

```bash
source .venv/bin/activate
```

### 4. Install the project

```bash
pip install -e .
```

### 5. Install development dependencies

```bash
pip install pytest
```

### 6. PostgreSQL requirements

For PostgreSQL backup and restore operations, install PostgreSQL client utilities and ensure `pg_dump` and `pg_restore` are available in your system PATH.

A PostgreSQL server and suitable database permissions are required for actual database operations.

## Usage

Run InfraPilot using Python's module interface:

```bash
python -m infrapilot --help
```

### System Monitoring

Display system information:

```bash
python -m infrapilot --info
```

Check system health:

```bash
python -m infrapilot --health
```

Generate a JSON report:

```bash
python -m infrapilot --report
```

Start continuous monitoring:

```bash
python -m infrapilot --monitor
```

Set a custom monitoring interval:

```bash
python -m infrapilot --monitor --interval 5
```

Stop continuous monitoring with `Ctrl + C`.

### Network Diagnostics

Display network information:

```bash
python -m infrapilot --network
```

Perform a DNS lookup:

```bash
python -m infrapilot --dns example.com
```

Ping a host:

```bash
python -m infrapilot --ping example.com
```

Set the ping count:

```bash
python -m infrapilot --ping example.com --count 5
```

### File and Directory Automation

Create a directory:

```bash
python -m infrapilot --create-dir test_directory
```

Create a file:

```bash
python -m infrapilot --create-file test.txt --content "Hello InfraPilot"
```

List a directory:

```bash
python -m infrapilot --list-dir .
```

Get file or directory information:

```bash
python -m infrapilot --path-info test.txt
```

Move a file or directory:

```bash
python -m infrapilot --move source.txt destination.txt
```

### Bash Automation

Validate a Bash script:

```bash
python -m infrapilot --validate-bash examples/bash_environment_demo.sh
```

Execute a trusted Bash script:

```bash
python -m infrapilot --run-bash examples/bash_environment_demo.sh
```

### PostgreSQL Backup and Restore

Create a database backup:

```bash
python -m infrapilot --pg-backup infrapilot_test --pg-user infrapilot_user
```

List available backups:

```bash
python -m infrapilot --pg-list-backups
```

Validate a backup archive:

```bash
python -m infrapilot --pg-validate-backup backups/backup.dump
```

Restore a backup into an existing database:

```bash
python -m infrapilot --pg-restore backups/backup.dump infrapilot_restore_test --pg-user infrapilot_user
```

Additional PostgreSQL options:

| Option | Purpose |
|---|---|
| `--pg-backup-dir` | Backup directory |
| `--pg-host` | PostgreSQL server host |
| `--pg-port` | PostgreSQL server port |
| `--pg-user` | PostgreSQL username |
| `--pg-timeout` | Operation timeout |

Use secure PostgreSQL authentication, such as a properly configured `.pgpass` file or another supported authentication method. Do not store database passwords in source code or commit them to Git.

## Health Status Logic

InfraPilot classifies resource utilization using the following thresholds:

| Resource Usage | Status |
|---|---|
| Below 75% | HEALTHY |
| 75% to below 90% | WARNING |
| 90% or above | CRITICAL |

Overall system health is determined by the most severe component status.

## Reports and Logs

Generated runtime files include:

- `logs/system_report.json` — System information and health report.
- `logs/infrapilot.log` — Application and health-check logs.
- `backups/` — PostgreSQL backup archives.

Runtime files should not be committed to the repository.

## Running Tests

Run the complete automated test suite:

```bash
python -m pytest -v
```

The current test suite contains **97 automated tests**, covering the implemented modules and PostgreSQL CLI integration.

## Project Goals

InfraPilot demonstrates practical experience with:

- Python infrastructure automation
- Linux system administration
- Bash scripting and execution
- Network diagnostics
- PostgreSQL backup and restore
- Logging and error handling
- Command-line application development
- Automated testing with Pytest
- Git and GitHub workflows

## Author

**Rukesh Kumar**

GitHub: https://github.com/Rukeshkumar914

Repository: https://github.com/Rukeshkumar914/infrapilot

## License

No open-source license has been added yet. Add an appropriate `LICENSE` file before distributing the project under an open-source license.
