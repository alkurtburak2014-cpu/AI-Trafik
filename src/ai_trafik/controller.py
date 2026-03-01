from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .config import SignalConfig


class SignalStage(Enum):
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    ALL_RED = "ALL_RED"


@dataclass(slots=True)
class SignalSnapshot:
    stage: SignalStage
    active_road: str
    remaining: float
    red_elapsed_a: float
    red_elapsed_b: float
    decision: str


class AdaptiveSignalController:
    """Adaptive controller with starvation guard and bounded green transitions."""

    def __init__(self, cfg: SignalConfig):
        cfg.validate()
        self.cfg = cfg
        self.active_road = "A"
        self.next_road = "B"
        self.stage = SignalStage.GREEN
        self.remaining = cfg.min_green
        self.last_green_duration = cfg.min_green

        self.smoothed_a = 0.0
        self.smoothed_b = 0.0

        self.red_elapsed_a = 0.0
        self.red_elapsed_b = 0.0

        self.last_decision = "Initialized"

    def _smooth_counts(self, count_a: float, count_b: float) -> None:
        a = self.cfg.smooth_alpha
        self.smoothed_a = a * count_a + (1.0 - a) * self.smoothed_a
        self.smoothed_b = a * count_b + (1.0 - a) * self.smoothed_b

    def _calc_green_duration(self, road: str) -> float:
        own = self.smoothed_a if road == "A" else self.smoothed_b
        other = self.smoothed_b if road == "A" else self.smoothed_a

        total = own + other
        if total < 0.1:
            raw = self.cfg.min_green
        else:
            own_ratio = own / total
            load_factor = min(1.0, own / 12.0)
            urgency = 0.65 * own_ratio + 0.35 * load_factor
            raw = self.cfg.min_green + (self.cfg.max_green - self.cfg.min_green) * urgency

        target = max(self.cfg.min_green, min(self.cfg.max_green, raw))

        step = self.cfg.max_green_step
        lo = max(self.cfg.min_green, self.last_green_duration - step)
        hi = min(self.cfg.max_green, self.last_green_duration + step)
        return max(lo, min(hi, target))

    def _update_red_elapsed(self, dt: float) -> None:
        color_a, color_b = self.colors()
        self.red_elapsed_a = self.red_elapsed_a + dt if color_a == "RED" else 0.0
        self.red_elapsed_b = self.red_elapsed_b + dt if color_b == "RED" else 0.0

    def _choose_next_road(self) -> str:
        if self.red_elapsed_a >= self.cfg.max_red and self.red_elapsed_b >= self.cfg.max_red:
            return "A" if self.smoothed_a >= self.smoothed_b else "B"
        if self.red_elapsed_a >= self.cfg.max_red:
            return "A"
        if self.red_elapsed_b >= self.cfg.max_red:
            return "B"
        return "B" if self.active_road == "A" else "A"

    def update(self, dt: float, count_a: float, count_b: float) -> None:
        self._smooth_counts(count_a, count_b)
        self._update_red_elapsed(max(0.0, dt))

        self.remaining -= dt
        if self.remaining > 0:
            return

        if self.stage == SignalStage.GREEN:
            self.stage = SignalStage.YELLOW
            self.remaining = self.cfg.yellow_time
            self.last_decision = f"Road {self.active_road} GREEN -> YELLOW"
            return

        if self.stage == SignalStage.YELLOW:
            self.stage = SignalStage.ALL_RED
            self.remaining = self.cfg.all_red_time
            self.next_road = self._choose_next_road()
            self.last_decision = f"Road {self.active_road} YELLOW -> ALL_RED"
            return

        self.active_road = self.next_road
        self.stage = SignalStage.GREEN
        new_green = self._calc_green_duration(self.active_road)
        self.last_green_duration = new_green
        self.remaining = new_green
        own = self.smoothed_a if self.active_road == "A" else self.smoothed_b
        other = self.smoothed_b if self.active_road == "A" else self.smoothed_a
        self.last_decision = f"Road {self.active_road} GREEN={new_green:.1f}s (own={own:.1f}, other={other:.1f})"

    def colors(self) -> tuple[str, str]:
        if self.stage == SignalStage.ALL_RED:
            return ("RED", "RED")
        if self.stage == SignalStage.GREEN:
            return ("GREEN", "RED") if self.active_road == "A" else ("RED", "GREEN")
        return ("YELLOW", "RED") if self.active_road == "A" else ("RED", "YELLOW")

    def phase_text(self) -> str:
        color_a, color_b = self.colors()
        return f"A:{color_a} B:{color_b} ({self.stage.value})"

    def snapshot(self) -> SignalSnapshot:
        return SignalSnapshot(
            stage=self.stage,
            active_road=self.active_road,
            remaining=self.remaining,
            red_elapsed_a=self.red_elapsed_a,
            red_elapsed_b=self.red_elapsed_b,
            decision=self.last_decision,
        )
