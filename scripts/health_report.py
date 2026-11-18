import json
from pathlib import Path

from infrapilot.health import check_system_health


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def main():
    report = check_system_health()

    report_json = json.dumps(report, indent=4)

    print(report_json)

    log_dir = PROJECT_ROOT / "logs"
    log_dir.mkdir(exist_ok=True)

    report_file = log_dir / "health_report.json"

    with report_file.open("w", encoding="utf-8") as file:
        file.write(report_json)

    print(f"\nReport saved to: {report_file}")


if __name__ == "__main__":
    main()
