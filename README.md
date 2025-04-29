# task_scheduler
This python program allows scheduling tasks in Validate &amp; RUNmode to check task completion time delta between the two modes

## Usage examples are as follows

Run the script from the command line with the following options:

```bash
python task_scheduler.py [-t TASK...] [--validate] [--run] [-h | --help]

Options
-t TASK..., --task TASK...: Specify a task. Each task specification should be in the format: name, duration, [dependency1, dependency2, ...].

name: name for the task.
duration: estimated duration of the task in seconds in integer values.
[dependency1, dependency2, ...]: A JSON list of task names to be completed prior to execution of this task. Use [] if no dependencies exist.
Note: Use of multiple -t or --task options is permitted.
--validate: task list verifcation for errors such as duplicate names

--run: Execute defined tasks

-h, --help: Show this help message and exit.


##Execution examples:

a> Task validation
!
python task_scheduler.py -t proc1,2,[] -t proc2,3,[proc1] --validate
Output:
Expected runtime: 5 seconds.

b> Execute tasks in run mode
!
python task_scheduler.py -t proc1,1,[] -t proc2,2,[] --run
Output:

Expected runtime: 3 seconds.
Executing task: proc1 (duration: 1 seconds)
Executing task: proc2 (duration: 2 seconds)
Task completed: proc1 (actual duration: ~1.00 seconds)
Task completed: proc2 (actual duration: ~2.00 seconds)
total runtime in run mode: ~2.00 seconds
Runtime delta between actual & expected: ~-1.00 seconds

c> Execute tasks with dependencies
!
python task_scheduler.py -t proc1,3,[] -t proc2,2,[proc1] --run
Expected Output:

Expected runtime: 5 seconds.
Executing task: procX (duration: 3 seconds)
Task completed: procX (actual duration: ~3.00 seconds)
Executing task: procY (duration: 2 seconds)
Task completed: procY (actual duration: ~2.00 seconds)
total runtime in run mode: ~5.00 seconds
Runtime delta between actual & expected: ~0.00 seconds
