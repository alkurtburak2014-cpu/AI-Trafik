from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SignalConfig:
    min_green: float = 12.0
    max_green: float = 55.0
    yellow_time: float = 3.0
    all_red_time: float = 1.0
    smooth_alpha: float = 0.35
    max_red: float = 75.0
    max_green_step: float = 8.0

    def validate(self) -> None:
        if self.min_green <= 0 or self.max_green <= 0:
            raise ValueError("green durations must be positive")
        if self.min_green > self.max_green:
            raise ValueError("min_green cannot exceed max_green")
        if self.yellow_time <= 0 or self.all_red_time < 0:
            raise ValueError("yellow_time must be > 0 and all_red_time must be >= 0")
        if not (0.01 <= self.smooth_alpha <= 1.0):
            raise ValueError("smooth_alpha must be in [0.01, 1.0]")
        if self.max_red <= 0:
            raise ValueError("max_red must be positive")
        if self.max_green_step <= 0:
            raise ValueError("max_green_step must be positive")
