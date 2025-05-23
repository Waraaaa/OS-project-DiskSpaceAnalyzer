import subprocess
import sys
import os
import shutil
import time
import csv
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

#==============================#
# Install required dependencies
#==============================#
def install_requirements():
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

# Try importing necessary packages
try:
    import psutil
    import matplotlib.pyplot as plt
    import matplotlib.ticker as ticker
except ImportError:
    print("Some packages are missing. Installing...")
    install_requirements()
    import psutil
    import matplotlib.pyplot as plt
    import matplotlib.ticker as ticker

#==============================#
# Convert bytes to human-readable format
def bytes_to_readable(size):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} PB"

#==============================#
# List all mounted drives
def list_drives():
    partitions = psutil.disk_partitions(all=False)
    return [p.device for p in partitions]

#==============================#
# Recursively calculate size of a directory
def get_size(path):
    total_size = 0
    for dirpath, _, filenames in os.walk(path, onerror=lambda e: None):
        for f in filenames:
            try:
                fp = os.path.join(dirpath, f)
                if not os.path.islink(fp):
                    total_size += os.path.getsize(fp)
            except Exception:
                pass
    return total_size

#==============================#
# Save benchmark result to CSV
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

#==============================#
# Display analysis result in terminal
def show_analysis(disk_data, total, used, free):
    print(f"\nTotal disk size: {bytes_to_readable(total)}")
    print(f"Used: {bytes_to_readable(used)}")
    print(f"Free: {bytes_to_readable(free)}\n")
    print(f"{'Directory':<30} {'Size':>10} {'% of Used':>12}")
    print("-" * 55)
    for data in disk_data:
        percent_used = (data["size"] / used * 100) if used > 0 else 0
        print(f"{data['path']:<30} {bytes_to_readable(data['size']):>10} {percent_used:>11.2f}%")

#==============================#
# Generate bar chart for disk usage
def plot(disk_data, base_path):
    disk_data = sorted(disk_data, key=lambda x: x["size"], reverse=True)
    paths = [item["path"] for item in disk_data]
    sizes = [item["size"] for item in disk_data]
    fig_height = max(5, 0.4 * len(disk_data))
    fig, ax = plt.subplots(figsize=(12, fig_height))
    bars = ax.barh(paths, sizes, color='skyblue')
    ax.invert_yaxis()
    ax.set_xlabel("Size")
    ax.set_title("Disk Usage by " + base_path)
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: bytes_to_readable(x)))
    for bar, size in zip(bars, sizes):
        ax.text(bar.get_width() + bar.get_width() * 0.01,
                bar.get_y() + bar.get_height() / 2,
                bytes_to_readable(size), va='center')
    plt.tight_layout()
    plt.grid(axis='x', linestyle='--', alpha=0.6)
    plt.show(block=False)

#==============================#
# Analyze a file or directory and get size
def scan_item(item_path):
    try:
        SKIP_EXTENSIONS = [".tmp"]
        _, ext = os.path.splitext(item_path)
        if ext.lower() in SKIP_EXTENSIONS:
            return None

        size = get_size(item_path) if os.path.isdir(item_path) else os.path.getsize(item_path)
        return {"path": item_path, "size": size}
    except Exception as e:
        print(f"{item_path:<30} ERROR: {e}")
        return None

#==============================#
# Analyze given path
def analyze(base_path="/"):
    print(f"Analyzing: {base_path}")
    start_time = time.time()

    total, used, free = shutil.disk_usage(base_path)
    scanned = set()
    disk_data = []

    # Filter duplicate real paths
    full_paths = []
    for item in os.listdir(base_path):
        item_path = os.path.join(base_path, item)
        real_path = os.path.realpath(item_path)
        if real_path not in scanned:
            scanned.add(real_path)
            full_paths.append(item_path)

    total_size_collected = 0
    item_count = 0

    # Use threading for concurrent scanning
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(scan_item, path) for path in full_paths]
        for future in as_completed(futures):
            result = future.result()
            if result:
                disk_data.append(result)
                item_count += 1
                total_size_collected += result["size"]

    elapsed_time = time.time() - start_time
    show_analysis(disk_data, total, used, free)
    plot(disk_data, base_path)
    log_benchmark(base_path, item_count, total_size_collected, elapsed_time)

#==============================#
# Handle drive selection when multiple are found
def input_case(drives):
    print("This program found more than 1 drive.")
    print("Please select the drive. Type the number:")
    while True:
        number = input()
        if number == "exit":
            exit()
        if number.isdigit() and 1 <= int(number) <= len(drives):
            return drives[int(number) - 1]
        else:
            print("Invalid drive. Please try again (\"exit\" to end program)")

#==============================#
# Main menu logic for navigation and analysis
def main():
    drives = list_drives()
    for i, d in enumerate(drives):
        print(f"{i + 1}: {d}")
    start_drive = "/" if len(drives) == 1 else input_case(drives)

    analyze(start_drive)

    old_path = start_drive
    path = start_drive
    while True:
        print("-" * 55)
        try:
            items = os.listdir(path)
        except Exception as e:
            print(f"Error accessing directory: {e}")
            path = old_path
            continue

        for i, item in enumerate(items):
            print(f"{i + 1}: {item}")
        print("Please enter a number to analyze that directory (\"exit\" to end, \"0\" to go back):")
        number = input()
        if number == "exit":
            exit()
        if number == "0":
            path = old_path
            continue
        if number.isdigit() and 1 <= int(number) <= len(items):
            old_path = path
            path = os.path.join(path, items[int(number) - 1])
            analyze(path)
        else:
            print("Invalid directory. Try again.")

#==============================#
if __name__ == "__main__":
    main()
