## CubeRTOS

## Description
A custom deterministic multi-threaded scheduler written in C that executes Python written tasks, ensuring predictable task ordering and timing. Custom software watchdog timers are used for each worker thread and the main scheduler to detect deadlocks, missed deadlines, and abnormal execution, enabling fault detection and recovery. 

## Usage
A blank requirements.txt is included for convenience. In my build, this file was populated with sensor-specific libraries used to collect mission data. For basic operation, the only required dependency is the standard json library, assuming you intend to use the provided helper functions for reading from and writing to .json files.

The project includes a custom Makefile to simplify the build process. Rather than invoking the Makefile directly, a shell script is provided to streamline rebuilding the project. Running ./cubeRTOSstart will clean the directory of any previously built artifacts and compile the software from scratch. Once the build completes, the main program can be launched with ./cubeRTOS, which will run continuously until terminated.

The scheduler dynamically allocates tasks and operating modes at runtime using the task.json configuration file. This allows the system behavior to be modified without recompilation. The format of the file is shown below:

```json
"modes": [
    {
        "PreFlight" : [
            {
                "name" : "task1.py",
                "period" : 1000,
                "priority" : 0,
                "released" : 1,
                "enabled" : true,
                "task_type" : "R"
            },
            {
                "name" : "task2.py",
                "period" : 10000,
                "priority" : 0,
                "released" : 1,
                "enabled" : true,
                "task_type" : "W"
            }
        ],
        "Flight" : [
            {
                "name" : "task1.py",
                "period" : 1000,
                "priority" : 0,
                "released" : 1,
                "enabled" : true,
                "task_type" : "U"
            }
        ]
    }
]
```
As shown above, multiple modes of operation can be defined, each containing the same or different sets of tasks. The maximum number of modes and tasks per mode is ultimately constrained by the underlying hardware. A task.json file used during the mission is included for reference, based on deployment on a Raspberry Pi Zero.

Most fields in task.json are self-describing. The only non-obvious field is task_type, which defines how the task is scheduled and what role it plays in the system.

The scheduler runs five concurrent threads, each with a dedicated responsibility. Two threads are used for reading data from sensors and writing to temporary data files. One thread is solely responsible for writing data to permanent storage, ensuring safe file access and preventing race conditions. The remaining two threads operate in tandem with a single duplex radio module: one handles uplinking incoming messages from the ground station, while the other manages downlinking beacons and image data from the satellite.

Operating modes may be defined and used as needed by the application. Each task is associated with a single, case-sensitive task_type character (R, W, U, or D), which determines how the scheduler assigns and executes the task.

Currently priority does not do anything, but I plan to eventually add preemption to this program. 

## Authors and acknowledgment
A special thanks for the Cube Sat Flight Laboratory and by extension, the Michigan Exploration Laboratory at the University of Michigan for giving me the opportunity to build and test this software. 

## Project status
As I am entering the second semester of my senior year at university, major updates to this codebase are unlikely in the foreseeable future.
