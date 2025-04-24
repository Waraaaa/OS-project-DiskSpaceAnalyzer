import subprocess
import sys
import os
import shutil
import psutil
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import time
import csv
from datetime import datetime

def bytes_to_readable(size):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} PB"

def list_drives():
    partitions = psutil.disk_partitions(all=False)
    return [p.device for p in partitions]


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

def show_analysis(disk_data, total, used, free):
    print(f"\nTotal disk size: {bytes_to_readable(total)}")
    print(f"Used: {bytes_to_readable(used)}")
    print(f"Free: {bytes_to_readable(free)}\n")
    print(f"{'Directory':<30} {'Size':>10} {'% of Used':>12}")
    print("-" * 55)
    for data in disk_data:
        percent_used = (data["size"] / used * 100) if used > 0 else 0
        print(f"{data['path']:<30} {bytes_to_readable(data['size']):>10} {percent_used:>11.2f}%")

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

    show_analysis(disk_data, total, used, free)
    plot(disk_data, base_path)
    log_benchmark(base_path, item_count, total_size_collected, elapsed_time)





