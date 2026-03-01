from __future__ import annotations

import logging
from dataclasses import dataclass

from .config import SignalConfig
from .controller import AdaptiveSignalController, SignalSnapshot

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class ServiceTickResult:
    snapshot: SignalSnapshot
    load_a: float
    load_b: float


class TrafficControlService:
    """Orchestrates controller updates and provides application-level entrypoints."""

    def __init__(self, config: SignalConfig):
        self.controller = AdaptiveSignalController(config)

    def tick(self, dt: float, load_a: float, load_b: float) -> ServiceTickResult:
        self.controller.update(dt=dt, count_a=load_a, count_b=load_b)
        snap = self.controller.snapshot()
        logger.debug(
            "tick stage=%s active=%s remaining=%.2f load_a=%.2f load_b=%.2f",
            snap.stage.value,
            snap.active_road,
            snap.remaining,
            load_a,
            load_b,
        )
        return ServiceTickResult(snapshot=snap, load_a=load_a, load_b=load_b)
