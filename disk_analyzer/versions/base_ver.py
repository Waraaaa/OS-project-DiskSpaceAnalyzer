import os
from utils.analyzer_helpers import (
    get_size, list_drives, show_analysis, bytes_to_readable
)
import time
import shutil

def analyze(base_path="/"):
    print(f"*** Base analyzer on {base_path} ***")
    start_time = time.time()

    total, used, free = shutil.disk_usage(base_path)
    scanned = set()
    disk_data = []
    item_count = total_size = 0

    for item in os.listdir(base_path):
        path = os.path.join(base_path, item)
        real = os.path.realpath(path)
        if real in scanned:
            continue
        scanned.add(real)

        try:
            if os.path.isdir(path):
                size = get_size(path)
            elif os.path.isfile(path):
                size = os.path.getsize(path)
            else:
                continue

            if os.path.splitext(item)[1].lower() == ".tmp":
                continue

            disk_data.append({"path": item, "size": size})
            item_count += 1
            total_size += size
        except Exception as e:
            print(f"Skipping {path}: {e}")

    elapsed = time.time() - start_time
    show_analysis(disk_data, total, used, free)
    plot(disk_data, base_path)
    log_benchmark(base_path, item_count, total_size, elapsed)

