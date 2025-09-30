import random
from functools import reduce

from agent._agent_utils import RoomStatus

class Environment:
	def __init__(self, num_rooms: int):
		self._BECOME_DIRTY_PROB: float = 0.1
		self._NUM_ROOMS: int = num_rooms
		self._rooms_status: list[RoomStatus] = [RoomStatus(random.randint(RoomStatus.CLEAN.value, RoomStatus.DIRTY_LEVEL_5.value)) for i in range(num_rooms)]

	@property
	def NUM_ROOMS(self):
		return self._NUM_ROOMS

	@property
	def rooms_status(self) -> list[RoomStatus]:
		return self._rooms_status

	def is_room_exist(self, room_index: int) -> bool:
		if not 0 <= room_index < self.NUM_ROOMS: return False
		return True

	def is_room_clean(self, room_index: int) -> bool:
		assert self.is_room_exist(room_index), "Invalid Room Index"
		
		if self._rooms_status[room_index] == RoomStatus.CLEAN: return True
		return False

	def are_all_rooms_clean(self) -> bool:
		for room in self._rooms_status:
			if room != RoomStatus.CLEAN: return False
		
		return True
	
	def get_num_dirty_rooms(self) -> int:
		return reduce(lambda acc, x: acc + 1 if x != RoomStatus.CLEAN else acc, self._rooms_status, 0)

	def get_room_dirtiness_level(self, room_index: int) -> RoomStatus:
		assert self.is_room_exist(room_index), "Invalid Room Index"
		return self._rooms_status[room_index]
	
	def suck_room(self, room_index: int) -> None:
		assert self.is_room_exist(room_index), "Invalid Room Index"
		self._rooms_status[room_index] = RoomStatus.CLEAN
	
	def randomly_make_clean_rooms_dirty(self) -> None:
		for i in range(self.NUM_ROOMS):
			if not self.is_room_clean(i): continue # skip dirty rooms
			if not random.random() < self._BECOME_DIRTY_PROB: continue #skip 90%
			
			# give a random dirtiness level
			self._rooms_status[i] = RoomStatus(random.randint(
				RoomStatus.DIRTY_LEVEL_1.value, RoomStatus.DIRTY_LEVEL_5.value
			))

	def get_rooms_status_log(self) -> str:
		log = ""
		for i, status in enumerate(self._rooms_status):
			log += f"\n\tRoom {i}: {status.name}"
		return log
