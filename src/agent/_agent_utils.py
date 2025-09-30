from enum import Enum, auto

from agent.agent_lang import *

class AgentAction(Enum):
	SUCK = 0
	MOVE_RIGHT = 1
	MOVE_LEFT = -1
	TURN_OFF = auto()

class ActionCost(Enum):
	MOVING = 2
	SUCKING_LEVEL_1 = 1
	SUCKING_LEVEL_2 = 2
	SUCKING_LEVEL_3 = 3
	SUCKING_LEVEL_4 = 4
	SUCKING_LEVEL_5 = 5

class RoomState:
	def __init__(self, room_index: int, is_room_clean: bool, dirtiness_level: RoomStatus):
		self._room_index: int = room_index
		self._is_room_clean: bool = is_room_clean
		self._dirtiness_level: RoomStatus = dirtiness_level

	@property
	def room_index(self) -> int:
		return self._room_index

	@property
	def is_room_clean(self) -> bool:
		return self._is_room_clean
	
	@property
	def dirtiness_level(self) -> RoomStatus:
		return self._dirtiness_level

class PerceivedState:
	def __init__(self, cur_room_state: RoomState, env_state: list[RoomStatus]):
		self._current_room_state: RoomState = cur_room_state
		self._environment_state: list[RoomStatus] = env_state
	
	@property
	def current_room_state(self) -> RoomState:
		return self._current_room_state
	
	@property
	def environment_state(self) -> list[RoomStatus]:
		return self._environment_state

class DecisionMade:
	def __init__(self, action: AgentAction, room_state: RoomState):
		self._on_room: RoomState = room_state
		self._action: AgentAction = action

	@property
	def on_room(self) -> RoomState:
		return self._on_room
	
	@property
	def action(self) -> AgentAction:
		return self._action
