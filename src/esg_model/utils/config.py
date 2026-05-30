from pathlib import Path
import yaml
from pydantic import BaseModel
from typing import Any

CONFIG_DIR = Path(__file__).resolve().parents[3] / "configs"


def load_yaml(name: str) -> dict[str, Any]:
    path = CONFIG_DIR / name
    with open(path) as f:
        return yaml.safe_load(f)


class Paths(BaseModel):
    raw: Path
    processed: Path
    features: Path

    @classmethod
    def from_config(cls) -> "Paths":
        cfg = load_yaml("data_sources.yaml")["storage"]
        p = cls(
            raw=Path(cfg["raw_path"]),
            processed=Path(cfg["processed_path"]),
            features=Path(cfg["features_path"]),
        )
        for d in (p.raw, p.processed, p.features):
            d.mkdir(parents=True, exist_ok=True)
        return p
