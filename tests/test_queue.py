import pytest

from src.core import Call, Floor
from src.elevator import ElevatorOPSAQueue


@pytest.mark.parametrize(
    "call",
    [
        Call(floor=Floor(1), destination=Floor(5)),
        Call(floor=Floor(3), destination=Floor(6)),
        Call(floor=Floor(1), destination=Floor(8)),
        Call(floor=Floor(6), destination=Floor(7)),
        Call(floor=Floor(1), destination=Floor(8)),
    ],
)
def test_linear_movement_up(call: Call, eda_queue: ElevatorOPSAQueue):
    eda_queue.add_request(call)
    previous_floor = eda_queue.current_floor
    while eda_queue.has_requests:
        eda_queue.determine_next()
        if eda_queue.current_floor in (call.floor, call.destination):
            assert eda_queue.stopped is True
        if eda_queue.current_floor == previous_floor:
            continue
        assert eda_queue.current_floor == previous_floor + 1
        assert eda_queue.current_floor < call.destination + 1

        previous_floor = eda_queue.current_floor


@pytest.mark.parametrize(
    "call",
    [
        Call(floor=Floor(1), destination=Floor(-5)),
        Call(floor=Floor(-3), destination=Floor(-6)),
        Call(floor=Floor(1), destination=Floor(-8)),
        Call(floor=Floor(-6), destination=Floor(-7)),
        Call(floor=Floor(-1), destination=Floor(-2)),
    ],
)
def test_linear_movement_down(call: Call, eda_queue: ElevatorOPSAQueue):
    eda_queue.add_request(call)
    previous_floor = eda_queue.current_floor
    while eda_queue.has_requests:
        eda_queue.determine_next()
        if eda_queue.current_floor == previous_floor:
            continue
        assert eda_queue.current_floor == previous_floor - 1
        assert eda_queue.current_floor > call.destination - 1
        if eda_queue.current_floor in (call.floor, call.destination):
            assert eda_queue.stopped is True
        previous_floor = eda_queue.current_floor


@pytest.mark.parametrize(
    "call",
    [
        Call(floor=Floor(3), destination=Floor(1)),
        Call(floor=Floor(5), destination=Floor(2)),
        Call(floor=Floor(7), destination=Floor(3)),
        Call(floor=Floor(8), destination=Floor(7)),
        Call(floor=Floor(8), destination=Floor(1)),
    ],
)
def test_movement_up_and_down(call: Call, eda_queue: ElevatorOPSAQueue):
    eda_queue.add_request(call)
    previous_floor = eda_queue.current_floor
    reverse_move = False
    while eda_queue.has_requests:
        eda_queue.determine_next()
        if eda_queue.current_floor == previous_floor:
            continue
        if reverse_move:
            assert previous_floor - 1 == eda_queue.current_floor
            assert eda_queue.current_floor > call.destination - 1
            previous_floor -= 1
        else:
            assert previous_floor + 1 == eda_queue.current_floor
            assert eda_queue.current_floor < call.floor + 1
            previous_floor += 1

        if eda_queue.current_floor == call.floor:
            reverse_move = True

        # Prevent checking destination floor first time.
        if ((eda_queue.current_floor == call.destination and reverse_move)
                or eda_queue.current_floor == call.floor):
            assert eda_queue.stopped is True
