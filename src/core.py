import abc
import enum
import typing as t
import uuid

import attrs

Floor = t.NewType("Floor", int)


class ElevatorStatus(enum.IntEnum):
    """Elevator status."""
    IDLE = 1
    IN_MOVEMENT = 2
    WAITING_ON_THE_FLOOR = 3


class DoorsStatus(enum.IntEnum):
    """Elevator doors status."""
    OPEN = 1
    CLOSED = 2


class Direction(enum.IntEnum):
    """Elevator direction."""
    UP = 1
    DOWN = 2


def get_opposite_direction(direction: Direction) -> Direction:
    if direction == Direction.UP:
        return Direction.DOWN
    return Direction.UP


@attrs.define
class Call:
    """Object of elevator call.

    Attrs:
        floor: Floor number from which the elevator is called
        destination: Floor number to which the elevator is called.
    """
    floor: Floor
    destination: Floor = attrs.field()

    @destination.validator
    def validate_destination(self, value, *args):
        if value == self.floor:
            raise ValueError("Destination floor cannot be equal to floor.")

    @property
    def direction(self) -> Direction:
        if self.destination > self.floor:
            return Direction.UP
        return Direction.DOWN


@attrs.define
class Passenger:
    call: Call | None = attrs.field()
    id: uuid.UUID = attrs.field(factory=uuid.uuid4, eq=True)


class ElevatorQueueAbstract(abc.ABC):
    """Implementation of algorithm for servicing elevator call queue."""

    @property
    @abc.abstractmethod
    def selected_floors(self) -> Floor:
        """Return selected floors inside of elevator."""

    @property
    @abc.abstractmethod
    def current_direction(self) -> Direction:
        """Return current direction."""

    @property
    @abc.abstractmethod
    def current_floor(self) -> Floor:
        """Return current floor."""

    @abc.abstractmethod
    def add_request(self, call: Call):
        """Add request to queue."""

    @property
    @abc.abstractmethod
    def stopped(self) -> bool:
        """Return queue movement status."""

    @abc.abstractmethod
    def determine_next(self):
        """Determine next queue state."""


class ElevatorAbstract(abc.ABC):

    MAX_FLOOR: int
    MIN_FLOOR: int
    CAPACITY: int

    @property
    @abc.abstractmethod
    def doors(self) -> DoorsStatus:
        """Return doors' status."""

    @property
    @abc.abstractmethod
    def status(self) -> ElevatorStatus:
        """Return elevator status."""

    @property
    @abc.abstractmethod
    def passengers(self) -> tuple[Passenger]:
        """Return passengers inside of elevator."""

    @property
    @abc.abstractmethod
    def capacity_left(self) -> int:
        """Return capacity left."""

    @abc.abstractmethod
    def enter_elevator(self, passenger: Passenger):
        """Enter passenger to elevator."""

    @abc.abstractmethod
    def exit_elevator(self, passenger: Passenger):
        """Exit passenger from elevator."""

    @property
    @abc.abstractmethod
    def current_direction(self) -> Direction | None:
        """Return current direction."""

    @property
    @abc.abstractmethod
    def current_floor(self) -> Floor:
        """Return current floor."""

    @property
    @abc.abstractmethod
    def selected_floors(self) -> tuple[Floor]:
        """Return selected floors."""

    @abc.abstractmethod
    def add_request(self, call: Call):
        """Add request to queue."""

    @abc.abstractmethod
    def move(self):
        """Move elevator."""
