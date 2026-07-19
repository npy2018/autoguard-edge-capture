from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

from .schemas import SignalFrame


@dataclass
class EvidenceRingBuffer:
    pre_event_frames: int = 50
    post_event_frames: int = 25
    _buffer: deque[SignalFrame] = field(init=False)
    _capture: list[SignalFrame] | None = field(default=None, init=False)
    _remaining: int = field(default=0, init=False)

    def __post_init__(self) -> None:
        self._buffer = deque(maxlen=self.pre_event_frames)

    def append(self, frame: SignalFrame) -> list[SignalFrame] | None:
        self._buffer.append(frame)
        if self._capture is None:
            return None
        self._capture.append(frame)
        self._remaining -= 1
        if self._remaining <= 0:
            result = self._capture
            self._capture = None
            return result
        return None

    def trigger(self) -> None:
        if self._capture is None:
            self._capture = list(self._buffer)
            self._remaining = self.post_event_frames

    @property
    def capturing(self) -> bool:
        return self._capture is not None
