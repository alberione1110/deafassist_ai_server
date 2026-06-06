from typing import Literal, Optional, TypedDict

WsDirection = Optional[
    Literal[
        "front",
        "back",
        "left",
        "right",
        "front_left",
        "front_right",
        "back_left",
        "back_right",
    ]
]

class InferenceMessage(TypedDict):
    type: str
    label: str
    score: float
    direction: WsDirection
    is_risk: bool
    timestamp: int
