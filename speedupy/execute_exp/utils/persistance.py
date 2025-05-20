import json, numbers
from pathlib import Path

SAMPLES_FILE = Path.home() / ".speedupy" / "samples.json"
SAMPLES_FILE.parent.mkdir(exist_ok=True)


def load_samples() -> dict:
    if SAMPLES_FILE.exists():
        with SAMPLES_FILE.open() as fh:
            return json.load(fh)
    return {}


def save_samples(samples: dict) -> None:
    with SAMPLES_FILE.open("w") as fh:
        json.dump(samples, fh, indent=2)

def make_serializable(d):
    return {
        k: [float(x) if isinstance(x, numbers.Number) else str(x) for x in v]
        for k, v in d.items()
    }
