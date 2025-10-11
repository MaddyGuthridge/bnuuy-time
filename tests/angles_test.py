import pytest

from bnuuy_time.buns import angle_diff


@pytest.mark.parametrize(
    ["a", "b", "expected"],
    [
        [1, 2, 1],
        [2, 1, 1],
        [359, 0, 1],
        [0, 359, 1],
    ],
)
def test_angle_diff(a, b, expected):
    assert angle_diff(a, b) == expected
