from __future__ import annotations

import argparse
import logging

from .config import SignalConfig
from .service import TrafficControlService


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="AI-Trafik adaptive controller demo CLI")
    p.add_argument("--min-green", type=float, default=12.0)
    p.add_argument("--max-green", type=float, default=55.0)
    p.add_argument("--yellow", type=float, default=3.0)
    p.add_argument("--all-red", type=float, default=1.0)
    p.add_argument("--max-red", type=float, default=75.0)
    p.add_argument("--smooth-alpha", type=float, default=0.35)
    p.add_argument("--max-green-step", type=float, default=8.0)
    p.add_argument("--dt", type=float, default=1.0)
    p.add_argument("--load-a", type=float, default=4.0)
    p.add_argument("--load-b", type=float, default=7.0)
    p.add_argument("--steps", type=int, default=8)
    p.add_argument("--log-level", default="INFO")
    return p


def main() -> None:
    args = build_parser().parse_args()
    logging.basicConfig(level=getattr(logging, str(args.log_level).upper(), logging.INFO))

    cfg = SignalConfig(
        min_green=args.min_green,
        max_green=args.max_green,
        yellow_time=args.yellow,
        all_red_time=args.all_red,
        max_red=args.max_red,
        smooth_alpha=args.smooth_alpha,
        max_green_step=args.max_green_step,
    )
    service = TrafficControlService(cfg)

    for _ in range(max(1, args.steps)):
        result = service.tick(args.dt, args.load_a, args.load_b)
        snap = result.snapshot
        print(
            f"phase={snap.stage.value} active={snap.active_road} remaining={snap.remaining:.1f}s "
            f"redA={snap.red_elapsed_a:.1f} redB={snap.red_elapsed_b:.1f} decision={snap.decision}"
        )


if __name__ == "__main__":
    main()
