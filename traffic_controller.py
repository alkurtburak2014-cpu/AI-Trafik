"""Backward-compatible imports for older paths."""

from ai_trafik.config import SignalConfig
from ai_trafik.controller import AdaptiveSignalController, SignalStage

__all__ = ["SignalConfig", "AdaptiveSignalController", "SignalStage"]
