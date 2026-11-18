"""Lightweight requests helper for API and hybrid UI/API checks."""
from typing import Any
import requests


class ApiHelper:
    def __init__(self, timeout: int = 30) -> None:
        self.timeout = timeout
        self.session = requests.Session()

    def get(self, url: str, expected_status: int = 200) -> requests.Response:
        response = self.session.get(url, timeout=self.timeout)
        if response.status_code != expected_status:
            raise AssertionError(
                f"GET {url} returned {response.status_code}; expected {expected_status}"
            )
        return response

    def verify_status(self, url: str, expected_status: int = 200) -> bool:
        try:
            return self.session.get(url, timeout=self.timeout).status_code == expected_status
        except requests.RequestException:
            return False

    def close(self) -> None:
        self.session.close()

