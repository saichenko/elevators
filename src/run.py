import random
from loguru import logger
from elevator import Call, DoorsStatus, Floor, Passenger, PassengerElevator
from exceptions import ElevatorFullError
import time

def make_decision() -> bool:
    """Return True if decided to add request."""
    return random.random() < 0.3


def generate_passenger_with_call(elevator: PassengerElevator) -> Passenger:
    min_floor = elevator.MIN_FLOOR
    max_floor = elevator.MAX_FLOOR
    floor, destination = random.sample(range(min_floor, max_floor + 1), 2)
    passenger = Passenger(
        call=Call(
            floor=Floor(floor),
            destination=Floor(destination),
        ),
    )
    return passenger


passengers_made_calls: list[Passenger] = []


def run():
    logger.info("Start simulation.")
    elevator = PassengerElevator(start_floor=Floor(1))
    while True:
        decision = make_decision()
        if decision is True:
            passenger = generate_passenger_with_call(elevator=elevator)
            elevator.add_request(passenger.call)
            passengers_made_calls.append(passenger)

        if elevator.doors == DoorsStatus.OPEN:
            for passenger in elevator.passengers:
                if elevator.current_floor == passenger.call.destination:
                    elevator.exit_elevator(passenger)

            for passenger in passengers_made_calls:
                if elevator.current_floor == passenger.call.floor:
                    try:
                        elevator.enter_elevator(passenger)
                        passengers_made_calls.remove(passenger)
                    except ElevatorFullError:
                        break

        elevator.move()
        time.sleep(1)


if __name__ == '__main__':
    run()
