import sys

from agent.agenticlean import AgentiClean
from agent.agent_lang import RunningState, RoomStatus
from environment import Environment


def main():
	num_rooms, T, T_digits = get_parameters()
	env = Environment(num_rooms)
	agent = AgentiClean(env, T)

	for timestamp in range(T):	
		print(f"\nTimestamp: {timestamp:0{T_digits}}")
		print("------------------------------------------------")
		
		agent_status = agent.run(timestamp)
		env_status = env.are_all_rooms_clean()
		env.randomly_make_clean_rooms_dirty()
		
		if should_simulation_end(T-timestamp-1, agent_status, env_status): break


def should_simulation_end(timestamp_left: int, agent_status: RunningState, env_status: bool) -> bool:
	assert agent_status != None and env_status != None, f"No Arguments Passed {timestamp_left}, {agent_status}, {env_status}"

	should_break = False
	if agent_status == RunningState.OFF:
		print("---------------------------------------------------------------")
		print("The agent runs out of usable energy, and cannot afford any further actions")
		should_break = True

	if env_status:
		print("---------------------------------------------------------------")
		print("All rooms are clean, and the agent has no meaningful actions left.")
		should_break = True

	if 0 == timestamp_left:
		print("---------------------------------------------------------------")
		print(f"The maximum number of steps is reached!")
		should_break = True
	
	if should_break:
		print("---------------------------------------------------------------")
		print("ending the simulation...")
		return True
	return False


def get_parameters():
	num = input("Enter the number of rooms exist: ")
	while(not check_input(num)): 
		num = input("Enter the number of rooms exist: ")

	num = int(num)

	T = input("Enter max. number of timestamps: ")
	while(not check_input(T)):
		T = input("Enter max. number of timestamps: ")

	T_digits = len(T)
	T = int(T)
	if T==0:
		print("\nexiting program... due to T = 0")
		sys.exit(0)

	return (num, T, T_digits)

def check_input(number: str) -> bool:
	if not number.isdigit():
		print("error: not a positive integer number!".upper(), end="\n\n")
		return False
	return True



if __name__ == "__main__":
	main()
