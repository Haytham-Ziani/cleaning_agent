from agent.agent_lang import *
from agent._agent_utils import *
from environment import Environment

class AgentiClean:
    def __init__(self, environment: Environment, max_running_time: int):
        self._running_state: RunningState = RunningState.ON
        self._environment: Environment = environment
        self._is_room_clean = self._environment.is_room_clean
        self._energy_level: float = 2.5 * self._environment.NUM_ROOMS
        self._current_location: int = 0
        self._num_rooms_cleaned: int = 0
        self._total_energy_consumed: float = 0
        self._action_history: list[AgentAction] = []   # keep action sequence

    def _set_running_state(self, new_state: RunningState) -> None:
        self._running_state = new_state

    def _change_location_to(self, direction: AgentAction) -> None:
        assert direction in (AgentAction.MOVE_RIGHT, AgentAction.MOVE_LEFT), \
            "Invalid move direction"
        assert self._environment.is_room_exist(self._current_location + direction.value)

        self._current_location += direction.value
        self._decrease_energy_level(ActionCost.MOVING.value)

    def _decrease_energy_level(self, amount: float) -> None:
        assert 0 < amount, "Invalid amount (should be greater than zero)" 
        assert self._can_afford_cost(amount), "Cannot decrease energy level: insufficient energy"
        self._energy_level -= amount
        self._total_energy_consumed += amount

    def _can_afford_cost(self, cost: float) -> bool:
        return self._energy_level >= cost

    def _can_move_right(self) -> bool:
        return self._environment.is_room_exist(self._current_location + 1)

    def _can_move_left(self) -> bool:
        return self._environment.is_room_exist(self._current_location - 1)

    def run(self, current_time: int) -> RunningState:
        if self._running_state == RunningState.OFF:
            return self._running_state

        state: PerceivedState = self._perceive()
        self.logInitialInfo(state.current_room_state)

        decision: DecisionMade = self._process(state)
        action: AgentAction = self._act(decision)

        self.logSubsequentInfo(action)
        return self._running_state

    def _perceive(self) -> PerceivedState:
        assert self._running_state != RunningState.OFF, "Agent is OFF"

        room_index = self._current_location
        is_room_clean = self._is_room_clean(room_index)
        dirtiness_level = self._environment.get_room_dirtiness_level(room_index)

        cur_room_state = RoomState(room_index, is_room_clean, dirtiness_level)
        state = PerceivedState(cur_room_state, self._environment.rooms_status)
        return state

    def _process(self, state: PerceivedState) -> DecisionMade:
        # Baseline rules:
        # 1. If current room dirty and enough energy → SUCK
        if (not state.current_room_state.is_room_clean and
            self._can_afford_cost(state.current_room_state.dirtiness_level.value)):
            return DecisionMade(AgentAction.SUCK, state.current_room_state)

        # 2. Else try to move right if possible
        if self._can_move_right() and self._can_afford_cost(ActionCost.MOVING.value):
            return DecisionMade(AgentAction.MOVE_RIGHT, state.current_room_state)

        # 3. Else try to move left if possible
        if self._can_move_left() and self._can_afford_cost(ActionCost.MOVING.value):
            return DecisionMade(AgentAction.MOVE_LEFT, state.current_room_state)

        # 4. Else → no action possible, shut down
        return DecisionMade(AgentAction.TURN_OFF, state.current_room_state)

    def _act(self, decision: DecisionMade) -> AgentAction:
        assert self._running_state != RunningState.OFF, "Agent is OFF"
        assert decision and decision.action and decision.on_room, "Invalid decision"

        match decision.action:
            case AgentAction.SUCK:
                self._suck(decision.on_room)
                self._set_running_state(RunningState.ON)
            case AgentAction.MOVE_LEFT:
                self._change_location_to(AgentAction.MOVE_LEFT)
                self._set_running_state(RunningState.ON)
            case AgentAction.MOVE_RIGHT:
                self._change_location_to(AgentAction.MOVE_RIGHT)
                self._set_running_state(RunningState.ON)
            case AgentAction.TURN_OFF:
                self._set_running_state(RunningState.OFF)
            case _:
                assert False, "Invalid action taken"

        # record action in history
        self._action_history.append(decision.action)
        return decision.action

    def _suck(self, room_state: RoomState) -> None:
        assert not room_state.is_room_clean, "Trying to suck a clean room"
        assert self._current_location == room_state.room_index, "Mismatch in room location"
        assert self._can_afford_cost(room_state.dirtiness_level.value), "Insufficient energy"

        self._environment.suck_room(room_state.room_index)
        self._decrease_energy_level(room_state.dirtiness_level.value)
        self._num_rooms_cleaned += 1

    def logInitialInfo(self, room_state: RoomState):
        w = 26
        running_status = f"{'Agent status:':<{w}} {self._running_state.name}\n"
        starting_energy = f"{'Starting energy level:':<{w}} {self._energy_level}\n"
        room_status = f"{f'Current Room {room_state.room_index} Status:':<{w}} {room_state.dirtiness_level.name}\n"
        print(running_status + starting_energy + room_status, end='')

    def logSubsequentInfo(self, action: AgentAction):
        w = 26
        last_action_made = f"{'Agent action:':<{w}} {action.name}\n"
        num_rooms_cleaned = f"{'Rooms cleaned so far:':<{w}} {self._num_rooms_cleaned}\n"
        remaining_energy = f"{'Remaining energy so far:':<{w}} {self._energy_level}\n"
        total_energy_consumed = f"{'Energy consumed so far:':<{w}} {self._total_energy_consumed}\n"
        rooms_state = f"{'Final rooms state:':<{w}} {self._environment.get_rooms_status_log()}\n"
        print(last_action_made + num_rooms_cleaned + remaining_energy + total_energy_consumed + rooms_state)

    def get_action_history(self) -> list[AgentAction]:
        return self._action_history

