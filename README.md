# task_scheduler
This python program allows scheduling tasks in Validate &amp; RUNmode to check task completion time delta between the two modes

## Usage examples are as follows

Run the script from the command line with the following options:

python task_scheduler.py [-t TASK...] [--validate] [--run] [-h | --help]

Options
-t TASK..., --task TASK...: Specify a task. Each task specification should be in the format: name, duration, [dependency1, dependency2, ...].

name: name of the task.

duration: estimated duration of the task in seconds in integer values.
[dependency1, dependency2, ...]: A JSON list of task names to be completed prior to execution of this task. Use [] if no dependencies exist.

Note: Use of multiple -t or --task options is permitted.

--validate: task list verifcation for errors such as duplicate names

--run: Execute defined tasks

-h, --help: Show this help message and exit.


##Execution examples:

a> Task validation
!
python tasksv1.py -t "proc_a,2,[]" --validate
Output expected:
!
Expected runtime: 2 seconds.

b> Execute multiple tasks in run mode with dependencies
!
python tasksv1.py -t "proc_a,2,[]" -t "proc_b,2,[\"proc_a\"]" --run
Output expected:

Expected runtime: 4 seconds.
Executing task: proc_a (duration: 2 seconds)
Task completed: proc_a (actual duration: ~2.00 seconds)
Executing task: proc_b (duration: 2 seconds)
Task completed: proc_b (actual duration: ~2.00 seconds)
total runtime in run mode: 4.01 seconds
Runtime delta between actual & expected: 0.01 seconds
