#======================================================
# Convert bytes into a human-readable format
def bytes_to_readable(size):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} PB"

#======================================================
# Display disk usage analysis in a formatted table
def show_analysis(disk_data, total, used, free):
    #--------------------------------------------------
    # 1) Print summary of total, used, and free disk space
    print(f"\nTotal disk size: {bytes_to_readable(total)}")
    print(f"Used: {bytes_to_readable(used)}")
    print(f"Free: {bytes_to_readable(free)}\n")

    #--------------------------------------------------
    # 2) Print header row for directory analysis
    print(f"{'Directory':<30} {'Size':>10} {'% of Used':>12}")
    print("-" * 55)

    #--------------------------------------------------
    # 3) Loop through disk data and print path, size, and percentage of used space
    for data in disk_data:
        percent_used = (data["size"] / used * 100) if used > 0 else 0
        print(f"{data['path']:<30} {bytes_to_readable(data['size']):>10} {percent_used:>11.2f}%")
