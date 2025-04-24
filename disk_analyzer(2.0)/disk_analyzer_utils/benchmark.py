#======================================================
# Imports required for logging system and process metrics
import os
import csv
from datetime import datetime
import psutil

#======================================================
# Function to log performance metrics into a CSV file
def log_benchmark(
    path,              # Path that was scanned
    item_count,        # Number of files/folders processed
    total_size,        # Aggregate size in bytes of all processed items
    elapsed_time,      # Time taken (in seconds) to complete the scan
    version,           # "base" or "optimized"
    filename="benchmark_log.csv"  # CSV file to append results to
):
    """
    Logs a detailed performance benchmark into a CSV file.
    Includes system and process stats at the time of logging.
    
    Metrics:
      - Program version ("base" vs "optimized")
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

    #======================================================
    # 1) Define the CSV header (only used when creating a new file)
    header = [
        "version", "timestamp", "path", "item_count", "total_size_bytes",
        "elapsed_time_sec", "cpu_percent", "mem_percent",
        "disk_read_bytes", "disk_write_bytes",
        "proc_read_bytes", "proc_write_bytes",
        "num_threads", "ctx_switches_vol", "ctx_switches_invol"
    ]

    #======================================================
    # 2) Collect system-wide CPU and memory usage
    cpu_pct = psutil.cpu_percent(interval=None)         # Percent CPU usage
    mem_pct = psutil.virtual_memory().percent           # Percent RAM used

    #======================================================
    # 3) Get global disk I/O stats (since system start)
    disk_io = psutil.disk_io_counters()
    disk_read_bytes = disk_io.read_bytes
    disk_write_bytes = disk_io.write_bytes

    #======================================================
    # 4) Get stats specific to the current Python process
    proc = psutil.Process()
    io = proc.io_counters()
    proc_read_bytes = io.read_bytes
    proc_write_bytes = io.write_bytes
    num_threads = proc.num_threads()
    ctx = proc.num_ctx_switches()
    ctx_vol = ctx.voluntary
    ctx_invol = ctx.involuntary

    #======================================================
    # 5) Prepare the row of data to write to CSV
    row = [
        version,
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

    #======================================================
    # 6) Append the row to the CSV file (add header if new file)
    write_header = not os.path.exists(filename)
    with open(filename, mode="a", newline="") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(header)
        writer.writerow(row)
