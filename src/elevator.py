import operator
import typing as t
from loguru import logger
import sys
from core import (Call, Direction, DoorsStatus, ElevatorAbstract,
                  ElevatorQueueAbstract, ElevatorStatus, Floor, Passenger,
                  get_opposite_direction)
from exceptions import (ElevatorDoorsClosedError, ElevatorFullError,
                        InvalidFloorError, PassengerNotInElevatorError)

logger.add(sys.stderr, format="{message} | {extra}")


def get_compare_operator(
        direction: Direction,
) -> t.Union[operator.gt, operator.lt]:
    """Return operator for comparing direction of floors."""
    if direction == Direction.UP:
        return operator.lt
    return operator.gt


class ElevatorOPSAQueue(ElevatorQueueAbstract):
    """Implementation of Optimal Passenger Sorting Algorithm.

    The algorithm that takes into account all passengers on all floors
    and aims to minimize waiting time and the number of stops. In this
    algorithm, the elevator seeks to optimize its movement by considering
    all passengers and their calls from different floors.
    """

    def __init__(self, start_floor: Floor):
        self.__requests: t.List[Call] = []
        self.__selected_floors: set[Floor] = set()
        self.__current_direction: Direction | None = None
        self.__current_floor = start_floor
        self.__stopped = False

    @property
    def current_floor(self) -> Floor:
        return self.__current_floor

    @property
    def stopped(self) -> bool:
        """Flag that indicates whether elevator is stopped or not"""
        return self.__stopped

    @property
    def current_direction(self) -> Direction | None:
        return self.__current_direction

    @property
    def selected_floors(self) -> tuple[Floor]:
        """Set of floors that were called inside."""
        return tuple(self.__selected_floors)

    def __get_farthest_request(self, in_current_direction: bool) -> Call:
        farthest = None
        for call in self.__requests:
            if in_current_direction and self.__compare_direction(
                    call.floor) != self.__current_direction:
                continue
            if farthest is None:
                farthest = call
                continue
            if (abs(call.floor - self.__current_floor) >
                    abs(farthest.floor - self.__current_floor)):
                farthest = call
        return farthest

    def __get_farthest_selected_floor(
            self,
            in_current_direction: bool,
    ) -> Floor:
        farthest = None
        for floor in self.selected_floors:
            if in_current_direction and self.__compare_direction(
                    floor) != self.__current_direction:
                continue
            if farthest is None:
                farthest = floor
                continue
            if (abs(floor - self.__current_floor) >
                    abs(floor - self.__current_floor)):
                farthest = floor
        return farthest

    def add_request(self, call: Call):
        logger.info("Request was added to queue.", extra={"call": call})
        self.__requests.append(call)

    @property
    def has_requests(self) -> bool:
        return bool(self.__requests) or bool(self.__selected_floors)

    def __compare_direction(self, floor: Floor) -> Direction:
        if self.__current_floor > floor:
            return Direction.DOWN
        return Direction.UP

    def __add_selected_floor(self, floor: Floor):
        logger.info(
            "Floor was added to selected floors.",
            extra={"floor": floor},
        )
        self.__selected_floors.add(floor)

    def __process_requests_to_stop(self) -> bool:
        floor = self.__current_floor
        direction = self.__current_direction

        requests_to_remove: list[Call] = []
        max_floor = max(self.__requests, key=lambda c: c.floor)

        for call in self.__requests:
            if direction == call.direction and floor == call.floor:
                requests_to_remove.append(call)

        if max_floor.floor == floor and max_floor.direction != direction:
            requests_to_remove.append(max_floor)

        if requests_to_remove:
            for call in requests_to_remove:
                self.__add_selected_floor(call.destination)
                self.__requests.remove(call)
            return True
        return False

    def __process_selected_floors_to_stop(self) -> bool:
        if self.__current_floor not in self.__selected_floors:
            return False
        self.__selected_floors.remove(self.__current_floor)
        return True

    def __need_to_stop(self) -> bool:
        """Check if elevator need to stop and process stoppage."""
        to_stop = False
        if self.__current_floor in self.__selected_floors:
            self.__selected_floors.remove(self.__current_floor)
            to_stop = True
        if self.__requests and self.__process_requests_to_stop():
            to_stop = True
        return to_stop

    def __get_new_direction(self) -> Direction | None:
        if not (self.__requests or self.__selected_floors):
            return None
        direction = self.__current_direction
        floor = self.__current_floor

        # Processing if requests.
        for request in self.__requests:
            compare = get_compare_operator(direction)
            if (request.direction == direction
                    and compare(self.current_floor, request.floor)):
                return direction

        # If only selected floors are left.
        if self.__selected_floors:
            if direction is None:
                farthest_call = self.__get_farthest_selected_floor(
                    in_current_direction=direction is not None,
                )
                if farthest_call > floor:
                    return Direction.UP
                return Direction.DOWN

            for call in self.__selected_floors:
                compare = get_compare_operator(direction)
                if (self.__compare_direction(call) == direction
                        and compare(floor, call)):
                    return direction
            return get_opposite_direction(direction)

        if direction is None or not self.__selected_floors:
            farthest_call = self.__get_farthest_request(
                in_current_direction=direction is not None,
            )
            if direction is not None and farthest_call is None:
                return get_opposite_direction(direction)

            if farthest_call.floor > floor:
                return Direction.UP
            elif farthest_call.floor == floor:
                return farthest_call.direction
            return Direction.DOWN

        return get_opposite_direction(direction)

    def __update_direction(self):
        self.__current_direction = self.__get_new_direction()

    def __set_next_floor(self):
        if self.__current_direction is None:
            return self.__current_floor
        if self.__current_direction == Direction.UP:
            self.__current_floor += 1
        else:
            self.__current_floor -= 1

    def determine_next(self):
        self.__set_next_floor()
        self.__stopped = self.__need_to_stop()
        self.__update_direction()
        logger.info(
            "Next floor was determined.",
            extra={
                "current_floor": self.__current_floor,
                "current_direction": self.__current_direction,
            },
        )


class PassengerElevator(ElevatorAbstract):

    MAX_FLOOR: int = 12
    MIN_FLOOR: int = 1
    CAPACITY: int = 10

    def __init__(self, start_floor: Floor | None):
        self.__queue = ElevatorOPSAQueue(start_floor or Floor(self.MIN_FLOOR))
        self.__status: ElevatorStatus = ElevatorStatus.IDLE
        self.__passengers: t.List[Passenger] = []

    @property
    def doors(self) -> DoorsStatus:
        if self.status == ElevatorStatus.WAITING_ON_THE_FLOOR:
            return DoorsStatus.OPEN
        return DoorsStatus.CLOSED

    @property
    def status(self) -> ElevatorStatus:
        return self.__status

    @property
    def passengers(self) -> tuple[Passenger]:
        return tuple(self.__passengers)

    @property
    def capacity_left(self) -> int:
        return self.CAPACITY - len(self.__passengers)

    def enter_elevator(self, passenger: Passenger):
        if self.doors == DoorsStatus.CLOSED:
            raise ElevatorDoorsClosedError
        if self.capacity_left < 1:
            logger.info("Elevator capacity was exceeded.")
            raise ElevatorFullError("Elevator capacity exceeded.")
        self.__passengers.append(passenger)

    def exit_elevator(self, passenger: Passenger):
        if self.doors == DoorsStatus.CLOSED:
            raise ElevatorDoorsClosedError
        if passenger in self.passengers:
            self.__passengers.remove(passenger)
            logger.info(
                "Passenger was exited from elevator.",
                extra={"passenger": passenger},
            )
            return
        logger.warning(
            "Passenger was not in elevator.",
            extra={"passenger": passenger},
        )
        raise PassengerNotInElevatorError

    @property
    def current_direction(self) -> Direction | None:
        return self.__queue.current_direction

    @property
    def current_floor(self) -> Floor:
        return self.__queue.current_floor

    @property
    def selected_floors(self) -> tuple[Floor]:
        return self.__queue.selected_floors

    def add_request(self, call: Call):
        min_floor = self.MIN_FLOOR
        max_floor = self.MAX_FLOOR
        if (min_floor >= call.floor <= max_floor and
                min_floor >= call.destination <= max_floor):
            raise InvalidFloorError(f"Please make sure that floor is "
                                    f"in range [{min_floor} , {max_floor}]")
        self.__queue.add_request(call)

    def move(self):
        self.__queue.determine_next()
        if not self.__queue.has_requests:
            self.__status = ElevatorStatus.IDLE
        elif self.__queue.stopped:
            self.__status = ElevatorStatus.WAITING_ON_THE_FLOOR
        else:
            self.__status = ElevatorStatus.IN_MOVEMENT
        logger.info("Elevator was moved.", extra={"status": self.__status})
