import os
import shutil
import time
import asyncio
import psutil
from disk_analyzer_utils.plotting import plot
from disk_analyzer_utils.benchmark import log_benchmark
from disk_analyzer_utils.utils import show_analysis

async def get_size(path):
    def compute_size():
        total = 0
        for dirpath, _, filenames in os.walk(path, onerror=lambda e: None):
            for f in filenames:
                try:
                    fp = os.path.join(dirpath, f)
                    if not os.path.islink(fp):
                        total += os.path.getsize(fp)
                except Exception:
                    pass
        return total

    return await asyncio.to_thread(compute_size)

async def scan_item(path):
    try:
        SKIP_EXTENSIONS = [".tmp"]
        _, ext = os.path.splitext(path)
        if ext.lower() in SKIP_EXTENSIONS:
            return None

        if os.path.isdir(path):
            size = await get_size(path)
        elif os.path.isfile(path):
            size = await asyncio.to_thread(os.path.getsize, path)
        else:
            return None

        return {"path": os.path.basename(path), "size": size}
    except Exception as e:
        print(f"{path:<30} ERROR: {e}")
        return None

async def analyze(base_path="/"):
    print(f"Analyzing: {base_path}")
    start_time = time.time()
    total, used, free = shutil.disk_usage(base_path)

    try:
        items = await asyncio.to_thread(os.listdir, base_path)
    except Exception as e:
        print(f"Error listing {base_path}: {e}")
        return

    scanned = set()
    full_paths = []
    for item in items:
        item_path = os.path.join(base_path, item)
        real_path = os.path.realpath(item_path)
        if real_path not in scanned:
            scanned.add(real_path)
            full_paths.append(item_path)

    tasks = [scan_item(path) for path in full_paths]
    results = await asyncio.gather(*tasks)

    disk_data = [r for r in results if r]
    item_count = len(disk_data)
    total_size = sum(d["size"] for d in disk_data)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Analyze time: {elapsed_time} s.")
    process = psutil.Process(os.getpid())
    print(f"Memory used: {process.memory_info().rss / 1024 ** 2:.2f} MB")

    show_analysis(disk_data, total, used, free)
    plot(disk_data, base_path)
    log_benchmark(base_path, item_count, total_size, elapsed_time)

async def analyzer(start_drive):
    nested_directory = 0
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
                await analyzer(path)
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
