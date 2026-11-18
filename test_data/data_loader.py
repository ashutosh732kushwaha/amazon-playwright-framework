"""JSON/CSV loading and deterministic Faker data factories."""
import csv
import json
from pathlib import Path
from typing import Any
from faker import Faker


class DataLoader:
    def __init__(self, data_dir: Path | None = None) -> None:
        self.data_dir = data_dir or Path(__file__).parent

    def json(self, name: str) -> Any:
        return json.loads((self.data_dir / name).read_text(encoding="utf-8"))

    def csv(self, name: str) -> list[dict[str, str]]:
        with (self.data_dir / name).open(encoding="utf-8", newline="") as handle:
            return list(csv.DictReader(handle))

    @staticmethod
    def fake_product(seed: int | None = None) -> dict[str, str]:
        faker = Faker()
        if seed is not None:
            Faker.seed(seed)
        return {"name": faker.catch_phrase(), "city": faker.city(), "email": faker.email()}

