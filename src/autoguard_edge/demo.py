from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from .detector import HybridEdgeTrigger
from .model import TinyLinearAutoencoder
from .schemas import SignalFrame


def build_baseline(seed: int = 7, samples: int = 500, window: int = 10) -> np.ndarray:
    rng = np.random.default_rng(seed)
    raw = np.column_stack(
        [
            rng.normal(0.55, 0.05, samples),
            rng.normal(0.0, 0.08, samples),
            rng.normal(0.0, 0.08, samples),
            rng.normal(0.0, 0.05, samples),
            rng.poisson(0.05, samples) / 5.0,
            np.clip(rng.normal(0.75, 0.08, samples), 0, 1),
        ]
    )
    return np.asarray([raw[i : i + window].reshape(-1) for i in range(samples - window)])


def run(output: Path | None = None) -> dict[str, object]:
    window = 10
    model = TinyLinearAutoencoder(components=5).fit(build_baseline(window=window))
    detector = HybridEdgeTrigger(model=model, window_size=window, threshold=0.65)
    frames: list[SignalFrame] = []
    for index in range(90):
        acceleration = -0.15
        jerk = 0.1
        ttc = 8.0
        if index == 55:
            acceleration = -4.2
            jerk = -5.8
            ttc = 1.3
        frames.append(
            SignalFrame(
                timestamp_s=index / 5,
                speed_mps=18.0,
                acceleration_mps2=acceleration,
                jerk_mps3=jerk,
                steering_angle_deg=1.2,
                planner_switches=0,
                min_ttc_s=ttc,
            )
        )
    event = None
    for frame in frames:
        event = detector.process(frame) or event
    if event is None:
        raise RuntimeError("demo did not emit an event")
    result = event.model_dump(mode="json")
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result
