import time
from typing import Optional
from app.config import RISK_LABELS

DIRECTION_MAP = {
    None: None,
    "F": "front",
    "B": "back",
    "L": "left",
    "R": "right",
    "FL": "front_left",
    "FR": "front_right",
    "BL": "back_left",
    "BR": "back_right",
}

def normalize_direction(direction: Optional[str]) -> Optional[str]:
    if direction is None:
        return None
    raw = str(direction).strip()
    if raw in DIRECTION_MAP:
        return DIRECTION_MAP[raw]
    upper = raw.upper()
    return DIRECTION_MAP.get(upper)

def build_inference_message(result: dict) -> dict:
    label = result.get("label")
    return {
        "type": "inference",
        "label": label,
        "score": result.get("score"),
        "direction": normalize_direction(result.get("direction")),
        "is_risk": label in RISK_LABELS,
        "timestamp": int(time.time()),
    }

def build_error_message(message: str) -> dict:
    return {
        "type": "error",
        "message": message,
        "timestamp": int(time.time()),
    }
