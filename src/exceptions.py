class ElevatorFullError(Exception):
    """Elevator capacity exceeded."""


class PassengerNotInElevatorError(Exception):
    """Passenger is not in elevator."""


class InvalidFloorError(Exception):
    """Floor is outside the acceptable range."""


class ElevatorDoorsClosedError(Exception):
    """Elevator doors are closed."""
