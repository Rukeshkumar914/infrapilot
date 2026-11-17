# InfraPilot

**InfraPilot** is a Python-based Linux infrastructure diagnostics and monitoring toolkit. It collects system information, evaluates system health, generates JSON reports, and continuously monitors CPU, memory, and disk usage.

## Features

- **System Information:** Collect hostname, operating system, Python version, CPU, memory, and disk information.
- **CPU Monitoring:** Monitor CPU usage percentage.
- **Memory Monitoring:** Track RAM usage and utilization.
- **Disk Monitoring:** Monitor disk capacity and usage.
- **Health Checks:** Classify system components as HEALTHY, WARNING, or CRITICAL.
- **Continuous Monitoring:** Perform recurring system health checks at a configurable interval.
- **JSON Reports:** Generate and save system information and health reports.
- **Logging:** Record monitoring events and health statuses in a log file.
- **Automated Testing:** Test project functionality using Pytest.

## Tech Stack

| Technology   | Purpose                    |
| ------------ | -------------------------- |
| Python       | Core programming language  |
| psutil       | System resource monitoring |
| Linux        | Operating environment      |
| Pytest       | Automated testing          |
| Git & GitHub | Version control            |

## Project Structure

```text
infrapilot/
├── backups/
├── config/
├── docs/
├── logs/
├── scripts/
├── src/
│   └── infrapilot/
│       ├── __init__.py
│       ├── __main__.py
│       ├── health.py
│       ├── logger.py
│       ├── monitor.py
│       └── system_info.py
├── tests/
│   ├── test_health.py
│   ├── test_logger.py
│   ├── test_report.py
│   └── test_system_info.py
├── pyproject.toml
├── .gitignore
└── README.md
```

## Installation

Clone the repository:

```bash
git clone https://github.com/Rukeshkumar914/infrapilot.git
cd infrapilot
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Linux:

```bash
source .venv/bin/activate
```

Install the project:

```bash
pip install -e .
```

Install the monitoring dependency if it is not included in the project dependencies:

```bash
pip install psutil
```

## Usage

Display system information:

```bash
python -m infrapilot --info
```

Check system health:

```bash
python -m infrapilot --health
```

Generate a JSON system report:

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

Stop monitoring with `Ctrl + C`.

## Health Status Logic

InfraPilot uses the following thresholds:

| Resource Usage   | Status   |
| ---------------- | -------- |
| Below 75%        | HEALTHY  |
| 75% to below 90% | WARNING  |
| 90% or above     | CRITICAL |

Overall system health is determined by the most severe component status.

## Reports and Logs

Generated files:

- `logs/system_report.json` — System information and health report.
- `logs/infrapilot.log` — Monitoring and health-check logs.

These runtime files are excluded from Git tracking.

## Running Tests

Run the test suite:

```bash
python -m pytest -v
```

The project currently has 10 automated tests.

## Project Goals

InfraPilot is a hands-on project for learning:

- Python automation
- Linux system administration
- Infrastructure monitoring
- Logging and diagnostics
- Automated testing
- CLI application development

## Future Improvements

Potential future enhancements:

- Configurable health thresholds
- Historical monitoring data
- Alert notifications
- Monitoring dashboard
- Exportable diagnostic reports

## Author

**Rukesh kumar**

GitHub: [Rukeshkumar914](https://github.com/Rukeshkumar914)

## License

Add a license file if you intend to distribute this project as open-source software.
