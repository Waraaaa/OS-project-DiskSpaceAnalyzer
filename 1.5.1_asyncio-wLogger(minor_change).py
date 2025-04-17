import subprocess
import sys

# Auto-install dependencies if missing
def install_requirements():
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

try:
    import os
    import shutil
    import psutil
    import matplotlib.pyplot as plt
    import matplotlib.ticker as ticker
    import time
    import csv
    import asyncio
    from datetime import datetime
except ImportError:
    print("Installing required packages...")
    install_requirements()
    import os
    import shutil
    import psutil
    import matplotlib.pyplot as plt
    import matplotlib.ticker as ticker
    import time
    import csv
    import asyncio
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

def show_analysis(disk_data, total, used, free):
    print(f"\nTotal disk size: {bytes_to_readable(total)}")
    print(f"Used: {bytes_to_readable(used)}")
    print(f"Free: {bytes_to_readable(free)}\n")
    print(f"{'Directory':<30} {'Size':>10} {'% of Used':>12}")
    print("-" * 55)
    for data in disk_data:
        percent_used = (data["size"] / used * 100) if used > 0 else 0
        print(f"{data['path']:<30} {bytes_to_readable(data['size']):>10} {percent_used:>11.2f}%")

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

def plot_paginated(data, base_path, page_size=20):
    import math

    data = sorted(data, key=lambda x: x["size"], reverse=True)
    total_pages = math.ceil(len(data) / page_size)

    for page in range(total_pages):
        start = page * page_size
        end = start + page_size
        chunk = data[start:end]

        paths = [item["path"] for item in chunk]
        sizes = [item["size"] for item in chunk]
        fig_height = max(5, 0.4 * len(chunk))

        fig, ax = plt.subplots(figsize=(12, fig_height))
        bars = ax.barh(paths, sizes, color='skyblue')
        ax.invert_yaxis()
        ax.set_xlabel("Size")
        ax.set_title(f"Disk Usage ({base_path}) — Page {page + 1}/{total_pages}")

        ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: bytes_to_readable(x)))

        for bar, size in zip(bars, sizes):
            ax.text(bar.get_width() + bar.get_width() * 0.01,
                    bar.get_y() + bar.get_height() / 2,
                    bytes_to_readable(size), va='center')

        plt.tight_layout()
        plt.grid(axis='x', linestyle='--', alpha=0.6)
        plt.show(block=False)

        print(f"\nShowing page {page + 1} of {total_pages}.")
        if page < total_pages - 1:
            input("Press Enter to show next page...")
            plt.close(fig)  # Only auto-close for middle pages
        else:
            print("Last page. Close the plot window manually to finish.")

def sync_get_size(start_path):
    total_size = 0
    for dirpath, _, filenames in os.walk(start_path, onerror=lambda e: None):
        for f in filenames:
            try:
                fp = os.path.join(dirpath, f)
                if not os.path.islink(fp):
                    total_size += os.path.getsize(fp)
            except Exception:
                pass
    return total_size

async def async_get_size(path):
    return await asyncio.to_thread(sync_get_size, path)

async def scan_item(item_path):
    try:
        SKIP_EXTENSIONS = [".tmp"]
        filename, ext = os.path.splitext(item_path)
        if ext.lower() in SKIP_EXTENSIONS:
            return None

        if os.path.isdir(item_path):
            size = await async_get_size(item_path)
        elif os.path.isfile(item_path):
            size = await asyncio.to_thread(os.path.getsize, item_path)
        else:
            return None

        return {"path": item_path, "size": size}
    except Exception as e:
        print(f"{item_path:<30} ERROR: {e}")
        return None

async def analyze(base_path="/"):
    print(f"Analyzing: {base_path}")
    start_time = time.time()

    total, used, free = shutil.disk_usage(base_path)
    scanned = set()
    disk_data = []

    try:
        items = os.listdir(base_path)
    except Exception as e:
        print(f"Error listing {base_path}: {e}")
        return

    full_paths = []
    for item in items:
        item_path = os.path.join(base_path, item)
        real_path = os.path.realpath(item_path)
        if real_path not in scanned:
            scanned.add(real_path)
            full_paths.append(item_path)

    tasks = [scan_item(path) for path in full_paths]
    results = await asyncio.gather(*tasks)

    item_count = 0
    total_size_collected = 0
    for r in results:
        if r:
            disk_data.append(r)
            item_count += 1
            total_size_collected += r["size"]

    end_time = time.time()
    elapsed_time = end_time - start_time

    show_analysis(disk_data, total, used, free)
    plot_paginated(disk_data, base_path)
    log_benchmark(base_path, item_count, total_size_collected, elapsed_time)

def input_case(drives):
    print("This program found more than 1 drive.")
    print("Please select the drive. Select the number: (\"exit\" to end program)")
    while True:
        number = input()
        if number == "exit": exit()
        if int(number) <= len(drives):
            return drives[int(number)-1]
        else:
            print("Invalid drive. Please try again (\"exit\" to end program)")

async def main():
    print("-" * 55)
    nested_directory = 0
    drives = list_drives()
    for i, d in enumerate(drives):
        print(f"{i+1}: {d}")
    start_drive = "/" if len(drives) == 1 else input_case(drives)

    await analyze(start_drive)
    nested_directory += 1

    old_path = [start_drive]
    path = start_drive
    while True:
        print("-" * 55)
        try:
            items = os.listdir(path)
            items = [item for item in items if os.path.isdir(os.path.join(path, item))]
        except Exception as e:
            print(f"Error accessing directory: {e}")
            path = old_path
            continue

        if len(items) == 0:
            print("No more directories in this directory (\"exit\" to end program, \"0\" to go back)")
        else: 
            for i in range(len(items)):
                print(f"{i+1}: {items[i]:3}")
            print("Please insert the number to continue analyze the selected directory (\"exit\" to end program, \"0\" to go back)")
        number = input()
        if number == "exit": exit()
        number = int(number)
        if number == 0:
            path = old_path[len(old_path)-1]
            old_path.pop()
            nested_directory -= 1
            if nested_directory == 0:
                await main()
                break
            else:
                continue
        if number <= len(items):
            old_path.append(path)
            path = os.path.join(path, items[int(number)-1])
        else:
            print("Invalid directory. Please try again (\"exit\" to end program, \"0\" to go back)")
            continue

        await analyze(path)
        nested_directory += 1


if __name__ == "__main__":
    asyncio.run(main())
