import math
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from disk_analyzer_utils.utils import bytes_to_readable

def plot(data, base_path, page_size=20):

    # 1) Sort descending by size so the largest items appear first
    data_sorted = sorted(data, key=lambda x: x["size"], reverse=True)

    # 2) Compute how many pages we’ll need
    total_pages = math.ceil(len(data_sorted) / page_size)

    # 3) Loop over each page
    for page in range(total_pages):
        # Determine slice of data for this page
        start = page * page_size
        end = start + page_size
        chunk = data_sorted[start:end]

        # Extract paths and sizes for plotting
        paths = [item["path"] for item in chunk]
        sizes = [item["size"] for item in chunk]

        # 4) Dynamically size the figure based on number of items
        fig_height = max(5, 0.4 * len(chunk))
        fig, ax = plt.subplots(figsize=(12, fig_height))

        # 5) Create horizontal bar chart
        bars = ax.barh(paths, sizes, color='skyblue')
        ax.invert_yaxis()  # Largest bar at top

        # 6) Label axes and title (include page indicator)
        ax.set_xlabel("Size")
        ax.set_title(f"Disk Usage ({base_path}) — Page {page + 1}/{total_pages}")

        # 7) Format X-axis ticks to human-readable sizes
        ax.xaxis.set_major_formatter(
            ticker.FuncFormatter(lambda x, _: bytes_to_readable(x))
        )

        # 8) Annotate each bar with its size label
        for bar, size in zip(bars, sizes):
            ax.text(
                bar.get_width() + bar.get_width() * 0.01,
                bar.get_y() + bar.get_height() / 2,
                bytes_to_readable(size),
                va='center'
            )

        # 9) Improve layout and add grid lines
        plt.tight_layout()
        plt.grid(axis='x', linestyle='--', alpha=0.6)

        # 10) Display non-blocking so code can continue
        plt.show(block=False)

        # 11) Pause between pages, closing intermediate figures
        print(f"\nShowing page {page + 1} of {total_pages}.")
        if page < total_pages - 1:
            input("Press Enter to show next page...")
            plt.close(fig)
        else:
            print("Last page. Close the plot window manually to finish.")
