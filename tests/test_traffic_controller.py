from traffic_controller import AdaptiveSignalController, SignalConfig, SignalStage


def tick_to_next_green(ctrl: AdaptiveSignalController, load_a: float, load_b: float) -> None:
    ctrl.update(ctrl.remaining + 0.01, load_a, load_b)  # GREEN->YELLOW
    ctrl.update(ctrl.remaining + 0.01, load_a, load_b)  # YELLOW->ALL_RED
    ctrl.update(ctrl.remaining + 0.01, load_a, load_b)  # ALL_RED->GREEN(next)


def test_green_duration_respects_bounds():
    cfg = SignalConfig(min_green=12.0, max_green=55.0, max_green_step=8.0)
    ctrl = AdaptiveSignalController(cfg)

    for _ in range(6):
        ctrl.update(0.1, 20.0, 1.0)

    d = ctrl._calc_green_duration("A")
    assert cfg.min_green <= d <= cfg.max_green


def test_starvation_guard_forces_waiting_road():
    cfg = SignalConfig(min_green=5.0, yellow_time=1.0, all_red_time=1.0, max_red=2.0)
    ctrl = AdaptiveSignalController(cfg)

    ctrl.active_road = "A"
    ctrl.stage = SignalStage.YELLOW
    ctrl.remaining = 0.0
    ctrl.red_elapsed_b = 2.1  # B has starved

    ctrl.update(0.1, 5.0, 1.0)  # YELLOW -> ALL_RED (chooses next road)
    assert ctrl.next_road == "B"

    ctrl.remaining = 0.0
    ctrl.update(0.1, 5.0, 1.0)  # ALL_RED -> GREEN(next)
    assert ctrl.active_road == "B"


def test_max_green_step_limits_jumps():
    cfg = SignalConfig(min_green=12.0, max_green=55.0, max_green_step=3.0)
    ctrl = AdaptiveSignalController(cfg)
    ctrl.last_green_duration = 20.0
    ctrl.smoothed_a = 50.0
    ctrl.smoothed_b = 0.1

    d = ctrl._calc_green_duration("A")
    assert d <= 23.0
    assert d >= 17.0
