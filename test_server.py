
import json
import threading
import unittest
from urllib.request import urlopen
from urllib.error import HTTPError
from unittest.mock import patch
from http.server import HTTPServer

from server import StatusHandler


class TestStatusAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.httpd = HTTPServer(("127.0.0.1", 0), StatusHandler)
        cls.port = cls.httpd.server_address[1]

        cls.thread = threading.Thread(
            target=cls.httpd.serve_forever,
            daemon=True,
        )
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        cls.thread.join()

    def test_status_returns_valid_json(self):
        url = f"http://127.0.0.1:{self.port}/status"

        with urlopen(url) as response:
            self.assertEqual(response.status, 200)
            self.assertIn(
                "application/json",
                response.headers["Content-Type"],
            )
            data = json.loads(response.read().decode("utf-8"))

        self.assertIn("hostname", data)
        self.assertIn("system", data)
        self.assertIn("cpu", data)
        self.assertIn("usage_percent", data["cpu"])
        self.assertGreaterEqual(data["cpu"]["usage_percent"], 0)
        self.assertLessEqual(data["cpu"]["usage_percent"], 100)
        self.assertIn("memory", data)
        self.assertIn("disk", data)
        self.assertIn("uptime_hours", data)

    def test_unknown_path_returns_404(self):
        url = f"http://127.0.0.1:{self.port}/unknown"

        with self.assertRaises(HTTPError) as error:
            urlopen(url)

        self.assertEqual(error.exception.code, 404)

    @patch("server.get_status", side_effect=RuntimeError("Simulated failure"))
    def test_status_returns_500_when_status_generation_fails(self, mock_get_status):
        url = f"http://127.0.0.1:{self.port}/status"

        with self.assertRaises(HTTPError) as error:
            urlopen(url)

        self.assertEqual(error.exception.code, 500)

        data = json.loads(error.exception.read().decode("utf-8"))
        self.assertEqual(data, {"error": "Internal server error"})

if __name__ == "__main__":
    unittest.main()
