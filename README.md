# InfraPilot

InfraPilot is a Linux infrastructure diagnostics and automation toolkit built with Python.

## Features

- System hostname and OS information
- CPU information and usage monitoring
- RAM usage monitoring
- Disk usage monitoring
- Automated tests using Pytest

## Tech Stack

- Python 3.14
- Linux
- psutil
- Pytest
- Git

## Project Structure

```text
infrapilot/
├── backups/
├── config/
├── docs/
├── logs/
├── scripts/
├── src/
│   ├── __init__.py
│   └── infrapilot/
│       ├── __init__.py
│       └── system_info.py
├── tests/
│   └── test_system_info.py
├── .gitignore
└── README.md
