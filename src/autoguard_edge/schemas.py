from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, Field


class SignalFrame(BaseModel):
    timestamp_s: float
    speed_mps: float
    acceleration_mps2: float
    jerk_mps3: float
    steering_angle_deg: float
    planner_switches: int = 0
    min_ttc_s: float = 99.0


class TriggerDecision(BaseModel):
    triggered: bool
    severity: Literal["L0", "L1", "L2", "L3"]
    rule_hits: list[str] = Field(default_factory=list)
    model_score: float = 0.0
    combined_score: float = 0.0


class EventPacket(BaseModel):
    event_id: str
    created_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    decision: TriggerDecision
    frames: list[SignalFrame]
    source: str
    evidence_uri: str
    notes: list[str] = Field(default_factory=list)
