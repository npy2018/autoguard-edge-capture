from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from uuid import uuid4

import numpy as np

from .model import TinyLinearAutoencoder
from .ring_buffer import EvidenceRingBuffer
from .rules import evaluate_rules
from .schemas import EventPacket, SignalFrame, TriggerDecision


@dataclass
class HybridEdgeTrigger:
    model: TinyLinearAutoencoder
    window_size: int = 10
    threshold: float = 0.72
    source: str = "edge-simulator"
    ring: EvidenceRingBuffer = field(default_factory=EvidenceRingBuffer)
    _features: deque[list[float]] = field(init=False)
    _pending_decision: TriggerDecision | None = field(default=None, init=False)

    def __post_init__(self) -> None:
        self._features = deque(maxlen=self.window_size)

    @staticmethod
    def features(frame: SignalFrame) -> list[float]:
        return [
            frame.speed_mps / 30.0,
            frame.acceleration_mps2 / 5.0,
            frame.jerk_mps3 / 8.0,
            frame.steering_angle_deg / 30.0,
            frame.planner_switches / 5.0,
            min(frame.min_ttc_s, 10.0) / 10.0,
        ]

    def process(self, frame: SignalFrame) -> EventPacket | None:
        self._features.append(self.features(frame))
        rules = evaluate_rules(frame)
        model_score = 0.0
        if len(self._features) == self.window_size:
            model_score = self.model.score(np.asarray(self._features, dtype=float).reshape(-1))
        rule_score = min(1.0, len(rules) * 0.35)
        combined = max(rule_score, 0.65 * model_score + 0.35 * rule_score)
        triggered = bool(rules) and combined >= self.threshold
        severity = "L0"
        if triggered:
            severity = "L3" if "low_ttc" in rules else "L2"
            self._pending_decision = TriggerDecision(
                triggered=True,
                severity=severity,
                rule_hits=rules,
                model_score=round(model_score, 4),
                combined_score=round(combined, 4),
            )
            self.ring.trigger()
        captured = self.ring.append(frame)
        if captured is not None and self._pending_decision is not None:
            event_id = f"EVT-{uuid4().hex[:12]}"
            packet = EventPacket(
                event_id=event_id,
                decision=self._pending_decision,
                frames=captured,
                source=self.source,
                evidence_uri=f"edge://{self.source}/{event_id}",
                notes=[
                    "The edge component records evidence; it does not attribute the event to OTA.",
                    "Complex OOD and root-cause analysis belong to the cloud pipeline.",
                ],
            )
            self._pending_decision = None
            return packet
        return None
