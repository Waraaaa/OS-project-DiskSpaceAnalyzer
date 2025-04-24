#======================================================
# Imports
# Standard libraries for filesystem, system info, time tracking, and async
import os
import sys
import shutil
import time
import asyncio
import psutil

# Custom utilities for plotting, logging, and displaying results
from disk_analyzer_utils.plotting import plot
from disk_analyzer_utils.benchmark import log_benchmark
from disk_analyzer_utils.utils import show_analysis

#======================================================
# Asynchronously calculate the total size of a folder
async def get_size(path):
    # Move heavy computation to a thread so it doesn't block the event loop
    def compute_size():
        total = 0
        for dirpath, _, filenames in os.walk(path, onerror=lambda e: None):
            for f in filenames:
                try:
                    fp = os.path.join(dirpath, f)
                    if not os.path.islink(fp):  # Skip symbolic links
                        total += os.path.getsize(fp)
                except Exception:
                    pass  # Ignore unreadable files
        return total

    return await asyncio.to_thread(compute_size)

#======================================================
# Asynchronously analyze the size of a single file or folder
async def scan_item(path):
    try:
        SKIP_EXTENSIONS = [".tmp"]
        _, ext = os.path.splitext(path)
        if ext.lower() in SKIP_EXTENSIONS:
            return None  # Skip unwanted file types

        # If it's a directory, calculate folder size
        if os.path.isdir(path):
            size = await get_size(path)
        # If it's a file, get the size directly
        elif os.path.isfile(path):
            size = await asyncio.to_thread(os.path.getsize, path)
        else:
            return None  # Skip non-file, non-folder items

        return {"path": os.path.basename(path), "size": size}
    except Exception as e:
        print(f"{path:<30} ERROR: {e}")
        return None  # Return None for failed items

#======================================================
# Asynchronously analyze contents of a directory
async def analyze(base_path="/"):
    print(f"Analyzing: {base_path}")
    start_time = time.time()

    # Get disk usage statistics for this drive
    total, used, free = shutil.disk_usage(base_path)

    # Try to get the list of items in the folder
    try:
        items = await asyncio.to_thread(os.listdir, base_path)
    except Exception as e:
        print(f"Error listing {base_path}: {e}")
        return

    # Track already scanned items (real path avoids double counting symbolic links)
    scanned = set()
    full_paths = []
    for item in items:
        item_path = os.path.join(base_path, item)
        real_path = os.path.realpath(item_path)
        if real_path not in scanned:
            scanned.add(real_path)
            full_paths.append(item_path)

    # Create tasks to scan all items concurrently
    tasks = [scan_item(path) for path in full_paths]
    results = await asyncio.gather(*tasks)

    # Filter out failed or skipped items
    disk_data = [r for r in results if r]
    item_count = len(disk_data)
    total_size = sum(d["size"] for d in disk_data)

    end_time = time.time()
    elapsed_time = end_time - start_time

    # Show analysis time and memory usage
    print(f"Analyze time: {elapsed_time} s.")
    process = psutil.Process(os.getpid())
    print(f"Memory used: {process.memory_info().rss / 1024 ** 2:.2f} MB")

    # Display the results
    show_analysis(disk_data, total, used, free)
    plot(disk_data, base_path)
    log_benchmark(base_path, item_count, total_size, elapsed_time, version="optimized")

#======================================================
# Asynchronous folder navigation loop with interactive selection
async def analyzer(start_drive):
    nested_directory = 0
    await analyze(start_drive)  # Analyze starting folder
    nested_directory += 1

    old_path = [start_drive]  # Stack to keep track of visited folders
    path = start_drive

    while True:
        print("-" * 55)
        try:
            # List directories only
            entries = os.listdir(path)
            dirs = [d for d in entries if os.path.isdir(os.path.join(path, d))]
        except Exception as e:
            print(f"Error accessing directory: {e}")
            # Go back one level if directory cannot be accessed
            if len(old_path) > 1:
                path = old_path.pop()
                nested_directory -= 1
                continue
            else:
                sys.exit(1)

        # Print folder choices or a message if none are available
        if not dirs:
            print('No more subdirectories here. ("exit" to end, "0" to go back)')
        else:
            for idx, d in enumerate(dirs, start=1):
                print(f"{idx}: {d}")
            print('Select a directory number ("exit" to end, "0" to go back):')

        # Get user input
        choice = input("> ").strip()
        if choice.lower() == "exit":
            sys.exit(0)

        # Go back to parent folder
        if choice == "0":
            if nested_directory == 1:
                # Restart from top-level directory
                return await analyzer(start_drive)
            elif old_path:
                path = old_path.pop()
                nested_directory -= 1
                continue
            else:
                continue

        # Handle number input
        try:
            num = int(choice)
        except ValueError:
            print(f'"{choice}" is not a valid number. Try again.')
            continue

        if num < 1 or num > len(dirs):
            print(f'"{num}" is out of range. Try again.')
            continue

        # Drill into selected folder
        old_path.append(path)
        path = os.path.join(path, dirs[num - 1])

        await analyze(path)
        nested_directory += 1
