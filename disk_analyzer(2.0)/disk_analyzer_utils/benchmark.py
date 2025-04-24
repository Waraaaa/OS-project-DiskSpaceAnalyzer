import os
import csv
from datetime import datetime
import psutil

def log_benchmark(
    path,              # Path that was scanned
    item_count,        # Number of files/folders processed
    total_size,        # Aggregate size in bytes of all processed items
    elapsed_time,      # Time taken (in seconds) to complete the scan
    filename="benchmark_log.csv"  # CSV file to append results to
):
    """
    Append a detailed performance row to a CSV with metrics including:
      - Timestamp
      - Path scanned
      - Item count and total size
      - Elapsed time
      - CPU and memory usage
      - System-wide disk I/O
      - Process-specific disk I/O
      - Thread count
      - Context-switch counts
    """

    # 1) Define header columns (only written if the file is new)
    header = [
        "timestamp", "path", "item_count", "total_size_bytes",
        "elapsed_time_sec", "cpu_percent", "mem_percent",
        "disk_read_bytes", "disk_write_bytes",
        "proc_read_bytes", "proc_write_bytes",
        "num_threads", "ctx_switches_vol", "ctx_switches_invol"
    ]

    # 2) Sample system-wide CPU and memory usage
    cpu_pct = psutil.cpu_percent(interval=None)         # CPU usage since last call
    mem_pct = psutil.virtual_memory().percent           # % of physical RAM used

    # 3) Sample system-wide disk I/O counters
    disk_io = psutil.disk_io_counters()                 # Cumulative since boot
    disk_read_bytes = disk_io.read_bytes                # Total bytes read
    disk_write_bytes = disk_io.write_bytes              # Total bytes written

    # 4) Sample this process’s I/O, thread count, and context switches
    proc = psutil.Process()                             # Current process handle
    io = proc.io_counters()                             # I/O specific to this process
    proc_read_bytes = io.read_bytes                     # Bytes this process read
    proc_write_bytes = io.write_bytes                   # Bytes this process wrote
    num_threads = proc.num_threads()                    # Thread count at end of run
    ctx = proc.num_ctx_switches()                       # Namedtuple of voluntary/involuntary
    ctx_vol = ctx.voluntary                             # Voluntary context switches
    ctx_invol = ctx.involuntary                         # Involuntary context switches

    # 5) Build the CSV row
    row = [
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        path,
        item_count,
        total_size,
        f"{elapsed_time:.4f}",
        f"{cpu_pct:.1f}",
        f"{mem_pct:.1f}",
        disk_read_bytes,
        disk_write_bytes,
        proc_read_bytes,
        proc_write_bytes,
        num_threads,
        ctx_vol,
        ctx_invol
    ]

    # 6) Append to CSV, writing header first if needed
    write_header = not os.path.exists(filename)
    with open(filename, mode="a", newline="") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(header)
        writer.writerow(row)

