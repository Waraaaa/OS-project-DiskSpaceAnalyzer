import os
import shutil
import time
import csv
from datetime import datetime
import psutil
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

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
# List all drives in the system (like C:\, D:\).
# =======================
def list_drives():
    partitions = psutil.disk_partitions(all=False)
    return [p.device for p in partitions]
      

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

        ax.xaxis.set_majorformatter(ticker.FuncFormatter(lambda x, : bytes_to_readable(x)))

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
