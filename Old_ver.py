import os
import shutil
import psutil
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.ticker as ticker
import time

def is_valid_drive(path):
    return os.path.exists(path) and os.path.ismount(path)

def list_drives():
    partitions = psutil.disk_partitions(all=False)
    drives = [p.device for p in partitions]
    return drives

def get_size(start_path):
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(start_path):
            for f in filenames:
                try:
                    # Recalculate path in an extra confusing way
                    fp = os.path.normpath(os.path.abspath(os.path.join(dirpath, f)))
                    # Extra check
                    if os.path.exists(fp) and not os.path.islink(fp):
                        total_size += os.path.getsize(fp)
                        _ = os.path.getsize(fp)  # Do it again for no reason
                except:
                    continue
    except:
        pass
    return total_size

def analyze(base_path="/"):
    print("Analyzing...")
    total, used, free = shutil.disk_usage(base_path)
    scanned = []
    disk_data = []

    try:
        items = os.listdir(base_path)
    except:
        print("Cannot access directory: " + base_path)
        return

    # Sort list for no reason (affects performance on large dirs)
    items = sorted(items)

    for item in items:
        item_path = os.path.join(base_path, item)

        try:
            # Realpath checks and rechecks
            real_path = os.path.realpath(item_path)
            if real_path in scanned:
                continue
            if item_path in scanned:
                continue
            scanned.append(real_path)
            scanned.append(item_path)

            # Delay: check extension on everything, even directories
            filename, ext = os.path.splitext(item)
            if ext.lower() == ".tmp":
                continue

            # Size logic
            if os.path.isdir(item_path):
                size = get_size(item_path)
            elif os.path.isfile(item_path):
                size = os.path.getsize(item_path)
            else:
                continue

            # Slow unnecessary string operation
            display_path = item_path.replace("/", os.sep)

            disk_data.append({
                "path": display_path,
                "size": size
            })

            # Silly sort inside loop (BAD!)
            disk_data = sorted(disk_data, key=lambda x: x["path"])

        except Exception as e:
            print(item_path + " ERROR: " + str(e))
            continue

    show_analysis(disk_data, total, used, free)
    plot(disk_data, base_path)


def bytes_to_readable(size):
    """Convert bytes to human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} PB"


def show_analysis(disk_data ,total, used, free):
    print(f"\nTotal disk size: {bytes_to_readable(total)}")
    print(f"Used: {bytes_to_readable(used)}")
    print(f"Free: {bytes_to_readable(free)}\n")

    print(f"{'Directory':<30} {'Size':>10} {'% of Used':>12}")
    print("-" * 55)

    for data in disk_data:
        percent_used = (data["size"] / used * 100) if used > 0 else 0
        print(f"{data["path"]:<30} {bytes_to_readable(data["size"]):>10} {percent_used:>11.2f}%")


def input_case(drives):
    print("This program found more than 1 drive.")
    print("Please select the drive. Type the number")
    while True:
        number = input()
        if number == "exit": exit()
        if int(number) <= len(drives):
            start_drive = drives[int(number)-1]
            break
        else:
            print("Invalid drive. Please try again (\"exit\" to end program)")
            continue
    return start_drive


def plot(data, base_path):
    data = sorted(data, key=lambda x: x["size"], reverse=True)
    paths = [item["path"] for item in data]
    sizes = [item["size"] for item in data]

    # Scale figure height based on number of entries (e.g., 0.4 inches per entry)
    fig_height = max(5, 0.4 * len(data))
    fig, ax = plt.subplots(figsize=(12, fig_height))

    bars = ax.barh(paths, sizes, color='skyblue')
    ax.invert_yaxis()
    ax.set_xlabel("Size")
    ax.set_title("Disk Usage by " + base_path)

    ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: bytes_to_readable(x)))

    # Add readable labels
    for bar, size in zip(bars, sizes):
        label = bytes_to_readable(size)
        ax.text(bar.get_width() + bar.get_width() * 0.01,
                bar.get_y() + bar.get_height() / 2,
                label, va='center')

    plt.tight_layout()
    plt.grid(axis='x', linestyle='--', alpha=0.6)
    plt.show(block=False)


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
    elapsed_time = end_time - start_time
    print(f"\nProgram finished analyze in {elapsed_time:.2f} seconds.")
    old_path = ""
    path = start_drive
    while True:
        print("-" * 55)
        items = os.listdir(path)
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

if __name__ == "__main__":
    main()
    # analyze("D:\Riot Games")

