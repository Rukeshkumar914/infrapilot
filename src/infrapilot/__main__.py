import json

from infrapilot.system_info import get_system_info
from infrapilot.health import check_system_health


def main():
    print("\n========== InfraPilot System Monitor ==========\n")

    system_info = get_system_info()
    health = check_system_health()

    print("SYSTEM INFORMATION")
    print(json.dumps(system_info, indent=4))

    print("\nSYSTEM HEALTH")
    print(json.dumps(health, indent=4))

    print("\n===============================================\n")


if __name__ == "__main__":
    main()
