
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

        return {"path": path, "size": size}
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

    show_analysis(disk_data, total, used, free)
    plot_paginated(disk_data, base_path)
    log_benchmark(base_path, item_count, total_size, time.time() - start_time)
