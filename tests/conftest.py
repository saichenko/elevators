import pytest


from src.core import Floor
from src.elevator import ElevatorEDAQueue


@pytest.fixture(scope="function")
def eda_queue() -> ElevatorEDAQueue:
    return ElevatorEDAQueue(start_floor=Floor(1))
