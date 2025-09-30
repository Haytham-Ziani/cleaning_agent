from enum import Enum, Flag, auto

class RoomStatus(Enum):
	CLEAN = 0
	DIRTY_LEVEL_1 = 1
	DIRTY_LEVEL_2 = 2
	DIRTY_LEVEL_3 = 3
	DIRTY_LEVEL_4 = 4
	DIRTY_LEVEL_5 = 5

class RunningState(Flag):
	ON = auto()
	OFF = auto()
	IDLE = auto()