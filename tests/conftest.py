import random

import pytest

from src.core import Call, Floor, Passenger
from src.elevator import PassengerElevator, ElevatorOPSAQueue


@pytest.fixture(scope="function")
def eda_queue() -> ElevatorOPSAQueue:
    return ElevatorOPSAQueue(start_floor=Floor(1))


@pytest.fixture(scope="function")
def elevator() -> PassengerElevator:
    return PassengerElevator(start_floor=Floor(1))


@pytest.fixture(scope="function")
def call(elevator) -> Call:
    floor, destination = random.sample(
        range(elevator.MIN_FLOOR, elevator.MAX_FLOOR + 1),
        2,
    )
    return Call(floor=Floor(floor), destination=Floor(destination))


@pytest.fixture(scope="function")
def passenger(call: Call) -> Passenger:
    return Passenger(call=call)
