
# Raspberry Pi Home Lab

A beginner-friendly home lab project built on Raspberry Pi 4 to practise Linux system administration, Python programming, HTTP APIs, and Git.

## Features

- Collects Linux system information.
- Reports memory usage and available memory.
- Reports root filesystem disk usage.
- Reports system uptime.
- Provides a JSON HTTP endpoint at `/status`.
- Returns HTTP 404 for unknown endpoints.

## Technologies

- Raspberry Pi 4
- Debian GNU/Linux 13
- Python 3
- Python standard library
- HTTP and JSON
- Git and GitHub

## Requirements

- Raspberry Pi or another Linux system
- Python 3
- A computer on the same network for testing

## Run the API

Clone the repository or open the project directory on your Raspberry Pi.

Start the server:

```bash
python3 server.py
```

Open the following URL from a browser on the same local network, replacing the IP address with your Raspberry Pi's address:

```text
http://<raspberry-pi-ip>:8000/status
```

The endpoint returns JSON containing the hostname, operating system, timestamp, memory information, disk usage, and uptime.

## Test error handling

Open an unknown endpoint, such as:

```text
http://<raspberry-pi-ip>:8000/test
```

The server should return HTTP 404.

## Project files

- `app.py` — command-line system status report.
- `server.py` — HTTP server that exposes system status as JSON.

## Learning outcomes

This project provides practical experience with Linux commands, Python file and system operations, HTTP request handling, JSON responses, SSH authentication, and Git version control.

## Future improvements

- Add automated tests.
- Improve error handling.
- Add structured logging.
- Run the API as a managed system service.
