from autoguard_edge.demo import run
from autoguard_edge.ring_buffer import EvidenceRingBuffer
from autoguard_edge.schemas import SignalFrame


def test_demo_emits_evidence_packet() -> None:
    result = run()
    assert result["decision"]["triggered"] is True
    assert "low_ttc" in result["decision"]["rule_hits"]
    assert result["evidence_uri"].startswith("edge://")
    assert len(result["frames"]) >= 50


def test_ring_buffer_captures_pre_and_post_frames() -> None:
    ring = EvidenceRingBuffer(pre_event_frames=3, post_event_frames=2)
    for i in range(3):
        ring.append(SignalFrame(timestamp_s=i, speed_mps=1, acceleration_mps2=0, jerk_mps3=0, steering_angle_deg=0))
    ring.trigger()
    assert ring.append(SignalFrame(timestamp_s=3, speed_mps=1, acceleration_mps2=0, jerk_mps3=0, steering_angle_deg=0)) is None
    result = ring.append(SignalFrame(timestamp_s=4, speed_mps=1, acceleration_mps2=0, jerk_mps3=0, steering_angle_deg=0))
    assert result is not None
    assert [frame.timestamp_s for frame in result] == [0, 1, 2, 3, 4]
