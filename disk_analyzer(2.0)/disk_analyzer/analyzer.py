import os
import sys
import shutil
import time
import psutil
from disk_analyzer_utils.plotting import plot
from disk_analyzer_utils.benchmark import log_benchmark
from disk_analyzer_utils.utils import show_analysis

def get_size(start_path):
    total_size = 0
    for dirpath, _, filenames in os.walk(start_path, onerror=lambda e: None):  # Walk through subdirectories
        for f in filenames:
            try:
                fp = os.path.join(dirpath, f)
                if not os.path.islink(fp):  # For skipping symbolic links.
                    total_size += os.path.getsize(fp)
            except Exception:
                pass  # Skip those files that raise errors, like permission denied, etc.
    return total_size


def analyze(base_path="/"):
    print(f"Analyzing: {base_path}")
    start_time = time.time()

    total, used, free = shutil.disk_usage(base_path)
    scanned = set()  # To avoid re-scanning symbolic links or dirs that we already visit.
    disk_data = []  # Stores size data for each directory.
    item_count = 0
    total_size_collected = 0

    for item in os.listdir(base_path):
        item_path = os.path.join(base_path, item)
        try:
            real_path = os.path.realpath(item_path)
            if real_path in scanned:
                continue  # Skip if this path is already scanned.
            scanned.add(real_path)

            # Get size depending on whether it's a file or folder.
            if os.path.isdir(item_path):
                size = get_size(item_path)
            elif os.path.isfile(item_path):
                size = os.path.getsize(item_path)
            else:
                continue  # Will continue if not a file or directory.

            SKIP_EXTENSIONS = [".tmp"]  # Ignore temporary files
            _, ext = os.path.splitext(item)
            if ext.lower() in SKIP_EXTENSIONS:
                continue

            disk_data.append({"path": item, "size": size})
            item_count += 1
            total_size_collected += size

        except Exception as e:
            print(f"{item_path:<30} ERROR: {e}")

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Analyze time: {elapsed_time} s.")
    process = psutil.Process(os.getpid())
    print(f"Memory used: {process.memory_info().rss / 1024 ** 2:.2f} MB")

    show_analysis(disk_data, total, used, free)
    plot(disk_data, base_path)
    log_benchmark(base_path, item_count, total_size, elapsed_time, version="base")


def analyzer(start_drive):
    nested_directory = 0
    analyze(start_drive)
    nested_directory += 1

    old_path = [start_drive]
    path = start_drive

    while True:
        print("-" * 55)
        try:
            entries = os.listdir(path)
            dirs = [d for d in entries if os.path.isdir(os.path.join(path, d))]
        except Exception as e:
            print(f"Error accessing directory: {e}")
            # if we can't list, go back one level if possible
            if len(old_path) > 1:
                path = old_path.pop()
                nested_directory -= 1
                continue
            else:
                sys.exit(1)

        # Show prompt
        if not dirs:
            print('No more subdirectories here. ("exit" to end, "0" to go back)')
        else:
            for idx, d in enumerate(dirs, start=1):
                print(f"{idx}: {d}")
            print('Select a directory number to analyze ("exit" to end, "0" to go back):')

        # Prompt until valid
        choice = input("> ").strip()
        if choice.lower() == "exit":
            sys.exit(0)

        if choice == "0":
            if nested_directory == 1:
                # back at first level—restart from root drive
                return analyzer(start_drive)
            elif old_path:
                # pop back one level
                path = old_path.pop()
                nested_directory -= 1
                continue
            else:
                # nothing to go back to
                continue

        # Try parse integer
        try:
            num = int(choice)
        except ValueError:
            print(f'"{choice}" is not a valid number. Try again.')
            continue

        # Validate range
        if num < 1 or num > len(dirs):
            print(f'"{num}" is out of range. Try again.')
            continue

        # Drill down
        old_path.append(path)
        path = os.path.join(path, dirs[num - 1])
        analyze(path)
        nested_directory += 1

    





