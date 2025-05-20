import pickle
from pathlib import Path

SAMPLES_FILE = Path.home() / ".speedupy" / "samples.pkl"
SAMPLES_FILE.parent.mkdir(exist_ok=True)

def save_samples(samples: dict) -> None:
    with SAMPLES_FILE.open("wb") as fh:
        pickle.dump(samples, fh, protocol=pickle.HIGHEST_PROTOCOL)

def load_samples() -> dict:
    if SAMPLES_FILE.exists():
        with SAMPLES_FILE.open("rb") as fh:
            return pickle.load(fh)
    return {}
