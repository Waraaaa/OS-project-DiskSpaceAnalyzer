# More details in README.md 

# =======================
# Import important modules.
# =======================
import subprocess
import sys
import os

# =======================
# Auto-install required libraries from requirements.txt if they're not already installed.
# =======================
def install_requirements():
    try:
        # Try import necessary packages
        import psutil
        import matplotlib.pyplot as plt
        import pandas
    except ImportError:
        # If any import fails -> install from requirements.txt
        requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_path])

install_requirements()  # Run the installation def above.

# =======================
# Imports
# =======================
import os
import shutil
import psutil
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import time
import csv
from datetime import datetime

# =======================
# Converts byte size into --> e.g., KB, MB, GB.
# =======================
def bytes_to_readable(size):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} PB"

# =======================
# List all drives in the system (like C:\, D:\).
# =======================
def list_drives():
    partitions = psutil.disk_partitions(all=False)
    return [p.device for p in partitions]

# =======================
# Calculates the total size of all files in the selected directory (recursive).
# Will also ignores symbolic links (shortcuts or junctions) and inaccessible files.
# =======================
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

# =======================
# Logs the benchmark results into a CSV file.
# 1. path | 2. number of items | 3. total size | 4. time taken
# =======================
def log_benchmark(path, item_count, total_size, elapsed_time, filename="benchmark_log.csv"):
    header = ["timestamp", "path", "item_count", "total_size_bytes", "elapsed_time_sec"]
    log_row = [
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        path,
        item_count,
        total_size,
        f"{elapsed_time:.4f}"
    ]
    write_header = not os.path.exists(filename)
    with open(filename, mode="a", newline="") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(header)
        writer.writerow(log_row)

# =======================
# Displays summary of disk usage [ Total | Used | Free ] 
# and shows a table of each folder/file analyzed with their sizes and % usage.
# =======================
def show_analysis(disk_data, total, used, free):
    print(f"\nTotal disk size: {bytes_to_readable(total)}")
    print(f"Used: {bytes_to_readable(used)}")
    print(f"Free: {bytes_to_readable(free)}\n")
    print(f"{'Directory':<30} {'Size':>10} {'% of Used':>12}")
    print("-" * 55)
    for data in disk_data:
        percent_used = (data["size"] / used * 100) if used > 0 else 0
        print(f"{data['path']:<30} {bytes_to_readable(data['size']):>10} {percent_used:>11.2f}%")

# =======================
# Visualizes the size of folders/files with a horizontal bar chart.
# (Sorts data by size.)
# =======================
def plot(disk_data, base_path):
    disk_data = sorted(disk_data, key=lambda x: x["size"], reverse=True)  # Sort by size descending.
    paths = [item["path"] for item in disk_data]
    sizes = [item["size"] for item in disk_data]

    # Dynamic graph height depending on number of files/folders.
    fig_height = max(5, 0.4 * len(disk_data))  # Adjust height based on number of bars.
    fig, ax = plt.subplots(figsize=(12, fig_height))
    
    bars = ax.barh(paths, sizes, color='skyblue')
    ax.invert_yaxis()  # Largest will show on top.
    ax.set_xlabel("Size")
    ax.set_title("Disk Usage by " + base_path)

    # Format X-axis will show size (converted).
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: bytes_to_readable(x)))

    # Add text labels to the bars.
    for bar, size in zip(bars, sizes):
        ax.text(bar.get_width() + bar.get_width() * 0.01,
                bar.get_y() + bar.get_height() / 2,
                bytes_to_readable(size), va='center')
        
    plt.tight_layout()
    plt.grid(axis='x', linestyle='--', alpha=0.6)
    plt.show(block=False)  # Non-blocking show

# =======================
# Analyzes the contents of the selected directory.
# Will gathers size data for each file/folder and stores it in a list.
# Also checks for duplicate symlinks and unwanted extensions.
# Then shows a summary and also the result plot.
# =======================
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

# =======================
# If found multiple drives, asks the user to select which one to scan. 
# Then will returns the selected drive path.
# =======================
def input_case(drives):
    print("This program found more than 1 drive.")
    print("Please select the drive. Type the number:")
    while True:
        number = input()
        if number == "exit": exit()
        if int(number) <= len(drives):
            return drives[int(number)-1]
        else:
            print("Invalid drive. Please try again (\"exit\" to end program)")

# =======================
# The main control of the program.
# Will detects available drives and make the user select one.
# Then analyzes it and allows the user to navigate and analyze subdirectories interactively.
# =======================
def main():
    drives = list_drives()
    for i, d in enumerate(drives):
        print(f"{i+1}: {d}")
    start_drive = "/" if len(drives) == 1 else input_case(drives)

    # Show time used on the terminal interface.
    start_time = time.time()
    analyze(start_drive)  # Analyze the selected drive.
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"\nProgram finished analyze in {elapsed_time:.2f} seconds.")

    # Start interactive navigation to analyze deeper folders.
    old_path = start_drive
    path = start_drive
    while True:
        print("-" * 55)
        # If the file/folder is inaccessible, 
        # will automatically backs out and lets the user try something else.
        try:
            items = os.listdir(path)
        except Exception as e:
            print(f"Error accessing directory: {e}")
            path = old_path
            continue

        # Get input.
        for i in range(len(items)):
            print(f"{i+1}: {items[i]}")
        print("Please insert the number to continue analyze the selected directory (\"exit\" to end program, \"0\" to go back to previous directory)")
        number = input()
        if number == "exit": exit()
        if int(number) == 0:
            path = old_path
            continue
        if int(number) <= len(items):
            old_path = path
            path = os.path.join(path, items[int(number)-1])
        else:
            print("Invalid directory. Please try again (\"exit\" to end program, \"0\" to go back to previous directory)")
            continue

        analyze(path)

# =======================
# Entry point, only run if executed as a script (not imported).
# =======================
if __name__ == "__main__":
    main()
