import random

from elevator import Call, DoorsStatus, Floor, Passenger, PassengerElevator
from exceptions import ElevatorFullError


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


if __name__ == '__main__':
    run()
