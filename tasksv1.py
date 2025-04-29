import sys
import time
import ast
import json
import threading

def build_tasklist(task_string):
    """Extract task details (name, duration, dependencies) from command line."""
    try:
        parts = [part.strip() for part in task_string.split(',')]
        name, duration_str, dependencies_str = parts[0], parts[1], parts[2]
        duration = int(duration_str)
        dependencies = json.loads(dependencies_str) if dependencies_str else []
        return name, {'duration': duration, 'dependencies': dependencies}
    except (ValueError, json.JSONDecodeError, IndexError) as e:
        raise ValueError(f"Task format is invalid: '{task_string}'. Expected 'name, duration, [dep1, dep2, ...]'. Details: {e}")

def fetch_tasks(task_specs):
    """fetch task definitions."""
    tasks = {}
    if not task_specs:
        raise ValueError("Specify -t/--task to provide task details.")
    for spec in task_specs:
        name, details = build_tasklist(spec)
        if name in tasks:
            raise ValueError(f"Duplicate task name '{name}'.")
        tasks[name] = details
    return tasks

def check_dependencies(all_tasks):
    """Check for dependencies."""
    processing = set()
    processed = set()

    def _visit(task_name):
        processing.add(task_name)
        for dependency in all_tasks[task_name]['dependencies']:
            if dependency in processing:
                return True
            if dependency not in processed:
                if _visit(dependency):
                    return True
        processing.remove(task_name)
        processed.add(task_name)
        return False

    for task in all_tasks:
        if task not in processed:
            if _visit(task):
                raise ValueError("Dependency located in task list.")

def validate_dependencies(all_tasks):
    """Verify dependencies match respective tasks."""
    task_names = set(all_tasks.keys())
    for name, details in all_tasks.items():
        if details['dependencies']:
            undefined = [dep for dep in details['dependencies'] if dep not in task_names]
            if undefined:
                raise ValueError(f"Dependencies '{', '.join(undefined)}' of task '{name}' are not defined.")

def validate_tasks(tasks):
    """Check errors."""
    validate_dependencies(tasks)
    check_dependencies(tasks)
    return True

def calculate_runtime(tasks):
    """Calculate expected task completion times."""
    start_times = {}
    durations = {name: data['duration'] for name, data in tasks.items()}
    dependencies = {name: set(data['dependencies']) for name, data in tasks.items()}
    completed_tasks = set()
    total_expected_time = 0

    while len(completed_tasks) < len(tasks):
        runnable_tasks = []
        for task_name in tasks:
            if task_name not in completed_tasks and dependencies[task_name].issubset(completed_tasks):
                runnable_tasks.append(task_name)

        if not runnable_tasks and len(completed_tasks) < len(tasks):
            raise ValueError("Task scheduling error.")

        for task_name in runnable_tasks:
            start = 0
            if dependencies[task_name]:
                start = max([start_times[dep] + durations[dep] for dep in dependencies[task_name]])
            start_times[task_name] = start
            finish_time = start + durations[task_name]
            total_expected_time = max(total_expected_time, finish_time)
            completed_tasks.add(task_name)

    return total_expected_time

def run_task(name, details, completed, lock):
    """Execute tasks & capture runtimes."""
    print(f"Executing task: {name} (duration: {details['duration']} seconds)")
    time.sleep(details['duration'])
    with lock:
        completed.add(name)
    print(f"Task completed: {name} (actual duration: ~{details['duration']:.2f} seconds)")

def enable_mthreads(tasks):
    """Enable multithreading & perform parallel task execution."""
    start_time = time.time()
    completed = set()
    threads = []
    lock = threading.Lock()

    while completed != set(tasks.keys()):
        runnable_tasks = [(name, details) for name, details in tasks.items()
                          if name not in completed and set(details['dependencies']).issubset(completed)]

        if not runnable_tasks and completed != set(tasks.keys()):
            time.sleep(0.1)
            continue

        for name, details in runnable_tasks:
            thread = threading.Thread(target=run_task, args=(name, details, completed, lock))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()
        threads = []

    actual_runtime = time.time() - start_time
    return actual_runtime

def main():
    task_specs = []
    validate_mode = False
    run_mode = False

    if len(sys.argv) > 1:
        i = 1
        while i < len(sys.argv):
            arg = sys.argv[i]
            if arg == "-t" or arg == "--task":
                i += 1
                if i < len(sys.argv):
                    task_specs.append(sys.argv[i])
                else:
                    print("Error: task specification incomplete after -t/--task")
                    sys.exit(1)
            elif arg == "--validate":
                validate_mode = True
            elif arg == "--run":
                run_mode = True
            elif arg == "-h" or arg == "--help":
                print("Usage: python task_scheduler.py [-t TASK...] [--validate] [--run]")
                print("Options:")
                print("  -t TASK...       Task specification: name, duration, [dep1, dep2, ...]")
                print("                   (Many -t options can be specified)")
                print("  --validate       Verify the task list & print expected runtime.")
                print("  --run            Execute independent tasks in parallel.")
                sys.exit(0)
            else:
                print(f"Error: Unknown argument '{arg}'")
                sys.exit(1)
            i += 1

    try:
        if not task_specs and (validate_mode or run_mode):
            print("Error: Specify -t/--task to provide task details.")
            sys.exit(1)
        elif not (validate_mode or run_mode):
            print("Error: Specify either --validate or --run.")
            sys.exit(1)

        if task_specs:
            tasks = fetch_tasks(task_specs)
            validate_tasks(tasks)
            expected_runtime = calculate_runtime(tasks)

            if validate_mode:
                print(f"Expected runtime: {expected_runtime} seconds.")
            elif run_mode:
                print(f"Expected runtime: {expected_runtime} seconds.")
                actual_runtime_threaded = enable_mthreads(tasks)
                runtime_difference_threaded = actual_runtime_threaded - expected_runtime
                print(f"total runtime in run mode: {actual_runtime_threaded:.2f} seconds")
                print(f"Runtime delta between actual & expected: {runtime_difference_threaded:.2f} seconds")
            else:
                print("Please specify either --validate or --run.")
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
