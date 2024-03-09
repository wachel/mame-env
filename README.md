# MAME-Env
MAME-Env is a Python library designed to create a virtual environment for MAME (Multiple Arcade Machine Emulator) games. It allows users to interact with MAME games programmatically and processing actions and reading data from the MAME emulator.It can be uesed for create custom environments for machine learning applications, such as reinforcement learning.

# Features
* Interactive Environment: Interact with MAME through a Python interface,and compatibility with the Latest MAME(tested on 0.263)
* Memory Access: Read and write memory addresses of the running game.
* IO Control: Send input commands to the game, such as button presses and joystick movements.
* Asynchronous Client and Server: Communicate with multiple MAME instances concurrently.
* Lua Script Execution: Execute Lua scripts within the MAME environment.

# Installation
To install MAME-Env, simply clone this repository and install the required dependencies:

## File Descriptions
- `BaseType.py`: Contains some basic data type definitions, such as `DataType`, `Address`, `IOPort`, and `StepAction`.
- `Console.py`: Defines the `ConsoleProcess` class for starting and closing MAME emulator processes.
- `Client.py`: Defines the `AsyncClient` class for asynchronous communication with the MAME emulator.
- `Server.py`: Defines the `AsyncServer` class for receiving connection requests from the MAME emulator.
- `Kof98Env.py` and `SF2Env.py`: Example files demonstrating how to use the MAME-Env library to create a game environment and perform simple random actions.

## Usage
1. Install the [MAME emulator](https://www.mamedev.org/).
2. Add the path of the MAME emulator executable to the system environment variables, or specify `mame_bin_path` in the initialization parameters of the `ConsoleProcess` class.
3. Download the game ROM files and place them in `roms` path.

## Examples
The Kof98Env.py and SF2Env.py files in the examples/ directory demonstrates how to create an environment for the game "The King of Fighters '98" and "Street Fighter 2". It shows how to interact with the game, perform actions, and monitor game state variables.

## Contributing
Contributions to MAME-Env are welcome! Please submit pull requests for any bug fixes, feature enhancements, or documentation improvements.

## License
MAME-Env is released under the MIT License. See the LICENSE file for more details.

## Contact
For any questions, suggestions, or issues, please open an issue on the GitHub repository or contact the maintainers directly.