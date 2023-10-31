import typing as t
import operator

from core import Call, Direction, ElevatorQueueAbstract, Floor


def get_compare_operator(
        direction: Direction,
) -> t.Union[operator.gt, operator.lt]:
    """Return operator for comparing direction of floors."""
    if direction == Direction.UP:
        return operator.lt
    return operator.gt


class ElevatorEDAQueue(ElevatorQueueAbstract):
    """Implementation of EDA (Elevator Dispatching Algorithm) algorithm."""

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
        return self.__stopped

    @property
    def current_direction(self) -> Direction | None:
        return self.__current_direction

    @property
    def selected_floors(self) -> tuple[Floor]:
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

    def __get_farthest_selected_floor(self,
                                      in_current_direction: bool) -> Floor:
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
        self.__requests.append(call)

    @property
    def has_requests(self) -> bool:
        return bool(self.__requests) or bool(self.__selected_floors)

    def __compare_direction(self, floor: Floor) -> Direction:
        if self.__current_floor > floor:
            return Direction.DOWN
        return Direction.UP

    def __add_selected_floor(self, floor: Floor):
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
        """Check if elevator need to stop on current floor."""
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
                if self.__compare_direction(call) == direction and compare(
                        floor, call):
                    return direction
            return ~direction

        if direction is None or not self.__selected_floors:
            farthest_call = self.__get_farthest_request(
                in_current_direction=direction is not None,
            )
            if direction is not None and farthest_call is None:
                return ~direction

            if farthest_call.floor > floor:
                return Direction.UP
            elif farthest_call.floor == floor:
                return farthest_call.direction
            return Direction.DOWN

        return ~direction

    def __update_direction(self):
        self.__current_direction = self.__get_new_direction()

    def __set_next_floor(self) -> Floor | None:
        if self.__current_direction is None:
            return self.__current_floor
        if self.__current_direction == Direction.UP:
            self.__current_floor += 1
        else:
            self.__current_floor -= 1
        return self.__current_floor

    def determine_next(self):
        self.__set_next_floor()
        self.__stopped = self.__need_to_stop()
        self.__update_direction()
        self.__update_direction()
