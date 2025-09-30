# AgentiClean

An agent program that act on N number of rooms and clean them based on its utility functions that aims to conserving power while cleaning as much rooms as possible.

## Project Requirements

> ### Objective:
>
> Develop a Python-based intelligent agent that operates in a linear environment of configurable size, cleaning rooms with varying dirtiness levels while managing a limited, scaled energy budget efficiently.
>
> ### Environment Description:
>
> The environment contains N rooms, indexed from 0 to N-1. Each room may be:
> Clean, or
> Dirty with a dirtiness level between 1 and 5.
> The agent starts in room 0.
>
> ### Energy Constraints:
>
> The agent is assigned an initial energy of:
> Initial Energy = 2.5×N (e.g., for 10 rooms → 25 units).
>
> #### Energy costs:
>
> -   Suck (cleaning): costs equal to the room's dirtiness level (1–5).
> -   MoveLeft or MoveRight: cost = 2 units per move.
>
> The agent cannot take an action if it lacks the energy required for it.
>
> ### Agent Capabilities:
>
> #### Percepts:
>
> -   Current room index.
> -   Room state (clean or dirty).
> -   Dirtiness level (if dirty).
> -   Remaining energy.
>
> #### Actuators / Actions:
>
> -   Suck: Clean the current room.
> -   MoveLeft: Move to the previous room.
> -   MoveRight: Move to the next room.
>
> ### Simulation Rules:
>
> -   The agent operates in discreet timesteps, up to a max of T which is Parameter to be specified by the user (ex. 100).
> -   At each time step, any clean room has a 10% chance to become dirty again with a random dirtiness level.
> -   The simulation ends when either:
>     -   All rooms are clean, and the agent has no meaningful actions left (i.e., nothing to clean and no reason to move).
>     -   The agent runs out of usable energy, and cannot afford any further actions (Suck, MoveLeft, or MoveRight).
>     -   A maximum number of steps T (e.g., 100) is reached to prevent infinite loops.
>
> ### Basic Agent Behavior (Baseline):
>
> 1. If the current room is dirty and energy allows → Suck.
> 2. Else, move right (or left at the boundary) if enough energy.
> 3. Stop if no further action is possible.
>
> Advanced students can implement planning or heuristics to optimize energy use.
>
> ### Output Requirements:
>
> -   Final state of each room.
> -   Number of rooms cleaned.
> -   Total energy consumed.
> -   Final remaining energy.
> -   Sequence of actions taken.
