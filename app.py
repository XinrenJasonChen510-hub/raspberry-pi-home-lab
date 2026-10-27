import platform
import shutil
from datetime import datetime
from pathlib import Path

def get_memory_info():
    """Read memory information from Linux."""
    values = {}

    with open("/proc/meminfo", encoding="utf-8") as file:
        for line in file:
            key, value = line.split(":", 1)
            if key in ("MemTotal", "MemAvailable"):
                values[key] = int(value.strip().split()[0])

    total = values["MemTotal"]
    available = values["MemAvailable"]
    used = total - available

    return total, used, available


def get_uptime():
    """Return system uptime in seconds."""
    with open("/proc/uptime", encoding="utf-8") as file:
        return float(file.read().split()[0])


def main():
    total, used, available = get_memory_info()

    disk = shutil.disk_usage("/")
    uptime_seconds = get_uptime()

    print("Raspberry Pi Home Lab")
    print("---------------------")
    print(f"Hostname: {platform.node()}")
    print(f"System: {platform.system()}")
    print(f"Time: {datetime.now().isoformat(timespec='seconds')}")

    print("\nMemory")
    print(f"Total: {total / 1024:.0f} MiB")
    print(f"Used: {used / 1024:.0f} MiB")
    print(f"Available: {available / 1024:.0f} MiB")

    print("\nDisk (/)")
    print(f"Total: {disk.total / (1024**3):.2f} GiB")
    print(f"Used: {disk.used / (1024**3):.2f} GiB")
    print(f"Free: {disk.free / (1024**3):.2f} GiB")
    print(f"Usage: {disk.used / disk.total * 100:.1f}%")

    print("\nSystem Uptime")
    print(f"{uptime_seconds / 3600:.1f} hours")


if __name__ == "__main__":
    main()
