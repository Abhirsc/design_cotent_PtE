from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from difflib import SequenceMatcher
from pathlib import Path

from core.schemas import GenerationBatch, QualityReport, ReflectionEntry


ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
OUTPUTS_DIR = ROOT_DIR / "outputs"
HISTORY_FILE = DATA_DIR / "history.json"


def ensure_project_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    if not HISTORY_FILE.exists():
        HISTORY_FILE.write_text("[]\n", encoding="utf-8")


def load_history() -> list[dict]:
    ensure_project_dirs()
    try:
        return json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def append_history(entries: list[ReflectionEntry]) -> None:
    history = load_history()
    history.extend(entry.model_dump(mode="json") for entry in entries)
    HISTORY_FILE.write_text(json.dumps(history, indent=2), encoding="utf-8")


def save_batch_output(batch: GenerationBatch) -> Path:
    ensure_project_dirs()
    path = OUTPUTS_DIR / f"{batch.batch_id}.json"
    path.write_text(json.dumps(batch.model_dump(mode="json"), indent=2), encoding="utf-8")
    return path


def cleanup_expired_outputs(expiry_hours: int = 24) -> None:
    ensure_project_dirs()
    cutoff = datetime.now(timezone.utc) - timedelta(hours=expiry_hours)
    for path in OUTPUTS_DIR.glob("*.json"):
        modified = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
        if modified < cutoff:
            path.unlink(missing_ok=True)


def quality_report(entry: ReflectionEntry, history: list[dict]) -> QualityReport:
    similarities = []
    for old in history:
        previous = old.get("generated_quote", "")
        if not previous:
            continue
        similarities.append(SequenceMatcher(None, entry.generated_quote, previous).ratio())

    closest = max(similarities) if similarities else 0.0
    return QualityReport(
        quote_length=len(entry.generated_quote),
        caption_length=len(entry.caption),
        hashtag_count=len(entry.hashtags),
        duplicate_warning=closest >= 0.82,
        closest_similarity=closest,
    )
