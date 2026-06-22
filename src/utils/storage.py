"""File storage helpers."""
import json
import logging
from pathlib import Path
from datetime import date

logger = logging.getLogger(__name__)


def save_report(content: str, directory: Path, filename: str) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / filename
    path.write_text(content, encoding="utf-8")
    logger.info(f"Saved report: {path}")
    return path


def save_json(data: dict | list, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_json(path: Path) -> dict | list | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        logger.error(f"Failed to load JSON {path}: {e}")
        return None


def append_tracker_entry(tracker_dir: Path, entry: dict) -> None:
    """Append an entry to a tracker's JSONL log."""
    tracker_dir.mkdir(parents=True, exist_ok=True)
    log_path = tracker_dir / "history.jsonl"
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
