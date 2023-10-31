from core import Passenger, DoorsStatus
from elevator import PassengerElevator


def test_passenger_enter(elevator: PassengerElevator, passenger: Passenger):
    elevator.add_request(passenger.call)
    passenger_added = False
    while not passenger_added:
        if (elevator.current_floor == passenger.call.floor
                and elevator.doors == DoorsStatus.OPEN):
            elevator.enter_elevator(passenger)
            passenger_added = True
            assert passenger in elevator.passengers

        elevator.move()
