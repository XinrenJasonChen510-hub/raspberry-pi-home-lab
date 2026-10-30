import json
import logging
import platform
import shutil
import time
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

def get_cpu_usage():
    def read_cpu_times():
        with open("/proc/stat", encoding="utf-8") as file:
            cpu_line = file.readline()

        values = [int(value) for value in cpu_line.split()[1:]]

        idle = values[3] + values[4]
        total = sum(values)

        return total, idle

    previous_total, previous_idle = read_cpu_times()

    time.sleep(0.1)

    current_total, current_idle = read_cpu_times()

    total_delta = current_total - previous_total
    idle_delta = current_idle - previous_idle

    if total_delta <= 0:
        return 0.0

    usage = (total_delta - idle_delta) / total_delta * 100

    return round(max(0.0, min(100.0, usage)), 1)

def get_status():
    disk = shutil.disk_usage("/")

    with open("/proc/uptime", encoding="utf-8") as file:
        uptime_seconds = float(file.read().split()[0])
    
    return {
        "hostname": platform.node(),
        "system": platform.system(),
        "time": datetime.now().isoformat(timespec="seconds"),
	"cpu": {
            "usage_percent": get_cpu_usage(),
        },
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

        if self.path.split("?")[0] == "/":
            try:
                with open("index.html", "rb") as file:
                    response = file.read()

                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(response)))
                self.end_headers()
                self.wfile.write(response)

                logging.info("Dashboard request completed: 200")

            except FileNotFoundError:
                logging.exception("Dashboard file not found")
                self.send_error(404, "Dashboard not found")

            except Exception:
                logging.exception("Failed to serve dashboard")
                self.send_error(500, "Internal server error")

            return

        if self.path != "/status":
            logging.warning("Unknown endpoint requested: %s", self.path)
            self.send_error(404, "Endpoint not found")
            return

        try:
            response = json.dumps(get_status(), indent=2).encode("utf-8")

        except Exception:
            logging.exception("Failed to generate system status")

            error_response = json.dumps({
                "error": "Internal server error"
            }).encode("utf-8")

            self.send_response(500)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(error_response)))
            self.end_headers()
            self.wfile.write(error_response)
            return

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
