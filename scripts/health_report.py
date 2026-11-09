import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.infrapilot.health import check_system_health


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
