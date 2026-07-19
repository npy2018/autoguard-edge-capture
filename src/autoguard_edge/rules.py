from __future__ import annotations

from .schemas import SignalFrame


def evaluate_rules(frame: SignalFrame) -> list[str]:
    hits: list[str] = []
    if frame.acceleration_mps2 <= -3.0:
        hits.append("hard_brake")
    if abs(frame.jerk_mps3) >= 4.0:
        hits.append("jerk_spike")
    if abs(frame.steering_angle_deg) >= 18.0 and frame.speed_mps >= 8.0:
        hits.append("high_speed_steering")
    if frame.planner_switches >= 4:
        hits.append("planner_oscillation")
    if frame.min_ttc_s <= 1.5:
        hits.append("low_ttc")
    return hits
