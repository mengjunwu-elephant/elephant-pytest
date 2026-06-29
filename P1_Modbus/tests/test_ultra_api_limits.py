import pytest

from p1_modbus import ultra_api_limits as lim


def test_speed_in_range() -> None:
    lim.validate_speed(50)


def test_speed_out_of_range() -> None:
    with pytest.raises(ValueError):
        lim.validate_speed(0)


def test_joint_angle_out_of_range() -> None:
    with pytest.raises(ValueError):
        lim.validate_joint_angle(1, 200.0)


def test_validate_if_skips_when_disabled() -> None:
    lim.validate_if(False, lim.validate_speed, 0)


def test_validate_if_runs_when_enabled() -> None:
    with pytest.raises(ValueError):
        lim.validate_if(True, lim.validate_speed, 0)
