import json
import logging
import platform
import shutil
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
)

def get_memory_info():
    values = {}

    with open("/proc/meminfo", encoding="utf-8") as file:
        for line in file:
            key, value = line.split(":", 1)
            if key in ("MemTotal", "MemAvailable"):
                values[key] = int(value.strip().split()[0])

    total = values["MemTotal"]
    available = values["MemAvailable"]

    return {
        "total_mib": round(total / 1024),
        "used_mib": round((total - available) / 1024),
        "available_mib": round(available / 1024),
    }


def get_status():
    disk = shutil.disk_usage("/")

    with open("/proc/uptime", encoding="utf-8") as file:
        uptime_seconds = float(file.read().split()[0])
    
    return {
        "hostname": platform.node(),
        "system": platform.system(),
        "time": datetime.now().isoformat(timespec="seconds"),
        "memory": get_memory_info(),
        "disk": {
            "total_gib": round(disk.total / (1024 ** 3), 2),
            "used_gib": round(disk.used / (1024 ** 3), 2),
            "free_gib": round(disk.free / (1024 ** 3), 2),
            "usage_percent": round(disk.used / disk.total * 100, 1),
        },
        "uptime_hours": round(uptime_seconds / 3600, 1),
    }


class StatusHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        logging.info("Received request: %s", self.path)

        if self.path != "/status":
            logging.warning("Unknown endpoint requested: %s", self.path)
            self.send_error(404, "Endpoint not found")
            return

        response = json.dumps(get_status(), indent=2).encode("utf-8")

        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)

        logging.info("Status request completed: 200")

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8000), StatusHandler)
    print("System Status API running on port 8000")
    print("Endpoint: http://192.168.3.152:8000/status")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        server.server_close()
