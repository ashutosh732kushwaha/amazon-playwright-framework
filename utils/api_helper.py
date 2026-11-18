"""Lightweight requests helper for API and hybrid UI/API checks."""
from typing import Any
import requests


class ApiHelper:
    def __init__(self, timeout: int = 30) -> None:
        self.timeout = timeout
        self.session = requests.Session()

    def get_response(self, url: str) -> requests.Response:
        return self.session.get(url, timeout=self.timeout)

    def get(self, url: str, expected_status: int = 200) -> requests.Response:
        response = self.get_response(url)
        if response.status_code != expected_status:
            raise AssertionError(
                f"GET {url} returned {response.status_code}; expected {expected_status}"
            )
        return response

    def verify_status(self, url: str, expected_status: int = 200) -> bool:
        try:
            return self.get_response(url).status_code == expected_status
        except requests.RequestException:
            return False

    def close(self) -> None:
        self.session.close()

