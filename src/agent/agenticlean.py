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
        self._last_optimized_env: list[RoomStatus] = []  # keep track of env state used in calc optimal actions
        self._optimal_actions_rev: list[AgentAction] = []
        self._max_cleaned_room: int = 0
        self._max_running_time: int = max_running_time  # used to optimize plan
        self._action_history: list[AgentAction] = []    # NEW: store executed actions

    def _set_running_state(self, new_state: RunningState) -> None:
        self._running_state = new_state

    def _change_location_to(self, direction: AgentAction) -> None:
        assert direction == AgentAction.MOVE_RIGHT or direction == AgentAction.MOVE_LEFT, \
            "Can't move to other directions other than right or left"
        assert self._environment.is_room_exist(self._current_location + direction.value)

        self._current_location += direction.value
        self._decrease_energy_level(ActionCost.MOVING.value)

    def _decrease_energy_level(self, amount: float) -> None:
        assert 0 < amount, "Invalid amount (should be greater than zero)" 
        assert self._can_afford_cost(amount), "Cannot decrease energy level due insufficient energy"
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

        decision: DecisionMade = self._process(state, current_time)
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

    def _process(self, state: PerceivedState, current_time: int) -> DecisionMade:
        assert self._running_state != RunningState.OFF, "Agent is OFF"

        # find best plan to clean max. #rooms if env has changed
        if state.environment_state != self._last_optimized_env: 
            self._last_optimized_env = list(state.environment_state)
            self._max_cleaned_room, self._optimal_actions_rev = self._find_optimal_actions_rev(
                self._current_location, self._energy_level, state._environment_state, dict()
            )

        next_action = self._optimal_actions_rev.pop()  # get best action saved
        
        # follow the plan if we don't have more time to wait
        # or if we can clean all the rooms
        if (self._max_running_time - current_time <= len(self._optimal_actions_rev) or 
            self._max_cleaned_room >= self._environment.get_num_dirty_rooms()):
            return DecisionMade(next_action, state.current_room_state)

        # otherwise wait for env change if a near room is clean
        if (self._is_room_clean(self._current_location) or
            (self._can_move_right() and self._is_room_clean(self._current_location+1)) or
            (self._can_move_left() and self._is_room_clean(self._current_location-1))):
            
            self._optimal_actions_rev.append(next_action)  # return popped action
            return DecisionMade(AgentAction.TURN_IDLE, state.current_room_state)

        # fall back to the original plan
        return DecisionMade(next_action, state.current_room_state)

    def _find_optimal_actions_rev(
        self, current_position: int, energy_left: float, room_states: list[RoomStatus], cases: dict[tuple, tuple]
    ) -> tuple[int, list[AgentAction]]:
        """
        Find optimal solution among all possible paths/decision that will
        let the agent clean as many rooms as possible with its initial energy.
        Returns: (max_rooms_cleaned, self._optimal_actions_rev)
        """
        assert energy_left >= 0, "Energy left cannot be negative"
        assert self._environment.is_room_exist(current_position)
        
        # save current state if we didn't cover it yet
        state_key = (current_position, energy_left, tuple(room_states))
        if state_key in cases:
            return cases[state_key]  # skip duplicates
        
        max_cleaned_rooms: int = 0
        optimal_actions_rev = []

        if energy_left < min(ActionCost._value2member_map_.keys()):  # base case
            optimal_actions_rev = [AgentAction.TURN_OFF]
            cases[state_key] = (max_cleaned_rooms, optimal_actions_rev)
            return (max_cleaned_rooms, optimal_actions_rev)

        # Action 1: Suck current room
        if room_states[current_position] != RoomStatus.CLEAN:
            suck_cost = room_states[current_position].value
            if suck_cost <= energy_left: 
                new_rs = list(room_states)
                new_rs[current_position] = RoomStatus.CLEAN 
                cleaned, actions = self._find_optimal_actions_rev(
                    current_position, energy_left - suck_cost, new_rs, cases
                )
                total_cleaned = cleaned + 1
                if total_cleaned > max_cleaned_rooms:
                    max_cleaned_rooms = total_cleaned
                    optimal_actions_rev = actions + [AgentAction.SUCK]

        # Action 2: Move right
        if self._environment.is_room_exist(current_position+1) and energy_left >= ActionCost.MOVING.value:
            cleaned, actions = self._find_optimal_actions_rev(
                current_position+1, energy_left-ActionCost.MOVING.value, room_states, cases
            )
            if cleaned > max_cleaned_rooms:
                max_cleaned_rooms = cleaned
                optimal_actions_rev = actions + [AgentAction.MOVE_RIGHT]
        
        # Action 3: Move left
        if self._environment.is_room_exist(current_position-1) and energy_left >= ActionCost.MOVING.value:
            cleaned, actions = self._find_optimal_actions_rev(
                current_position-1, energy_left-ActionCost.MOVING.value, room_states, cases
            )
            if cleaned > max_cleaned_rooms:
                max_cleaned_rooms = cleaned
                optimal_actions_rev = actions + [AgentAction.MOVE_LEFT]
        
        # Action 4: TURN_OFF when no beneficial actions
        if not optimal_actions_rev:
            optimal_actions_rev = [AgentAction.TURN_OFF]

        cases[state_key] = (max_cleaned_rooms, optimal_actions_rev)
        return (max_cleaned_rooms, optimal_actions_rev)

    def _act(self, decision: DecisionMade) -> AgentAction:
        assert self._running_state != RunningState.OFF, "Agent is OFF"
        assert decision and decision.action and decision.on_room, "Invalid decision"

        assert decision.on_room.room_index == self._current_location, \
            "Agent is not in the room it will act on"

        match decision.action:
            case AgentAction.SUCK:
                self._suck(decision.on_room)
                self._last_optimized_env[decision.on_room.room_index] = RoomStatus.CLEAN
                self._set_running_state(RunningState.ON)
            case AgentAction.MOVE_LEFT:
                self._change_location_to(AgentAction.MOVE_LEFT)
                self._set_running_state(RunningState.ON)
            case AgentAction.MOVE_RIGHT:
                self._change_location_to(AgentAction.MOVE_RIGHT)
                self._set_running_state(RunningState.ON)
            case AgentAction.TURN_OFF:
                self._set_running_state(RunningState.OFF)
            case AgentAction.TURN_IDLE:
                self._set_running_state(RunningState.IDLE)
            case _:
                assert False, "Invalid action taken"

        # NEW: record executed action
        self._action_history.append(decision.action)
        return decision.action

    def _suck(self, room_state: RoomState) -> None:
        assert not room_state.is_room_clean, "Sucking a cleaned room (it's already clean)"
        assert self._current_location == room_state.room_index, "Current room is not the room perceived"
        assert self._environment.is_room_exist(room_state.room_index), "Invalid Room Index"
        assert self._can_afford_cost(room_state.dirtiness_level.value), "Action can't be done due to low energy"
        
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

    # NEW: method to access full action sequence
    def get_action_history(self) -> list[AgentAction]:
        return self._action_history
