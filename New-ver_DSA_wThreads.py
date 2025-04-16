import os
import shutil
import psutil
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# =======================
# List all drives in the system.
# =======================
def list_drives():
    partitions = psutil.disk_partitions(all=False)
    drives = [p.device for p in partitions]
    return drives

# =======================
# Helper function to get size of one file safely
# =======================
def get_file_size(fp):
    try:
        if not os.path.islink(fp):  # Skip symbolic links
            return os.path.getsize(fp)
    except Exception:
        pass
    return 0

# =======================
# Multithreaded version of directory size calculator.
# Spawns threads to calculate file sizes in parallel.
# =======================
def get_size_threaded(start_path, max_workers=8):
    total_size = 0
    futures = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for dirpath, _, filenames in os.walk(start_path, onerror=lambda e: None):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                futures.append(executor.submit(get_file_size, fp))

        for future in as_completed(futures):
            total_size += future.result()

    return total_size

# =======================
# Convert bytes to human-readable string.
# =======================
def bytes_to_readable(size):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} PB"

# =======================
# Print summary and breakdown of disk usage.
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
# Analyzes the contents of the provided path using multithreaded size computation.
# =======================
def analyze(base_path="/"):
    print(f"Analyzing: {base_path}")
    total, used, free = shutil.disk_usage(base_path)
    scanned = set()
    disk_data = []

    for item in os.listdir(base_path):
        item_path = os.path.join(base_path, item)
        try:
            real_path = os.path.realpath(item_path)
            if real_path in scanned:
                continue  # Skip already scanned paths
            scanned.add(real_path)

            if os.path.isdir(item_path):
                size = get_size_threaded(item_path)  # <- Enhanced here
            elif os.path.isfile(item_path):
                size = os.path.getsize(item_path)
            else:
                continue

            SKIP_EXTENSIONS = [".tmp"]
            _, ext = os.path.splitext(item)
            if ext.lower() in SKIP_EXTENSIONS:
                continue

            disk_data.append({"path": item_path, "size": size})

        except Exception as e:
            print(f"{item_path:<30} ERROR: {e}")

    show_analysis(disk_data, total, used, free)
    plot(disk_data, base_path)

# =======================
# Handle user input when multiple drives are detected.
# =======================
def input_case(drives):
    print("This program found more than 1 drive.")
    print("Please select the drive. Type the number")
    while True:
        number = input()
        if number == "exit": exit()
        if int(number) <= len(drives):
            return drives[int(number)-1]
        else:
            print("Invalid drive. Please try again (\"exit\" to end program)")

# =======================
# Plots the data using a horizontal bar chart.
# =======================
def plot(data, base_path):
    data = sorted(data, key=lambda x: x["size"], reverse=True)
    paths = [item["path"] for item in data]
    sizes = [item["size"] for item in data]

    fig_height = max(5, 0.4 * len(data))
    fig, ax = plt.subplots(figsize=(12, fig_height))

    bars = ax.barh(paths, sizes, color='skyblue')
    ax.invert_yaxis()
    ax.set_xlabel("Size")
    ax.set_title("Disk Usage by " + base_path)

    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: bytes_to_readable(x)))

    for bar, size in zip(bars, sizes):
        label = bytes_to_readable(size)
        ax.text(bar.get_width() + bar.get_width() * 0.01,
                bar.get_y() + bar.get_height() / 2,
                label, va='center')

    plt.tight_layout()
    plt.grid(axis='x', linestyle='--', alpha=0.6)
    plt.show(block=False)

# =======================
# Program entry point. Lists drives, allows user selection, performs analysis, and allows navigation.
# =======================
def main():
    drives = list_drives()
    for i in range(len(drives)):
        print(f"{i+1}: {drives[i]}")
    start_drive = "/"
    if len(drives) > 1:
        start_drive = input_case(drives)

    start_time = time.time()
    analyze(start_drive)
    end_time = time.time()
    print(f"\nProgram finished analyze in {end_time - start_time:.2f} seconds.")

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
# Launch the program
# =======================
if __name__ == "__main__":
    main()
