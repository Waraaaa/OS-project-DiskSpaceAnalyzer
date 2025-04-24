#======================================================
# Imports for plotting
import math
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from disk_analyzer_utils.utils import bytes_to_readable

#======================================================
# Function to plot disk usage data in paginated horizontal bar charts
def plot(data, base_path, page_size=20):

    #======================================================
    # 1) Sort data by size in descending order
    data_sorted = sorted(data, key=lambda x: x["size"], reverse=True)

    #======================================================
    # 2) Calculate how many pages are needed based on the page size
    total_pages = math.ceil(len(data_sorted) / page_size)

    #======================================================
    # 3) Loop through each page and plot a subset of the data
    for page in range(total_pages):
        # Determine the start and end indices for the current page
        start = page * page_size
        end = start + page_size
        chunk = data_sorted[start:end]

        #======================================================
        # 4) Prepare data for plotting: paths and corresponding sizes
        paths = [item["path"] for item in chunk]
        sizes = [item["size"] for item in chunk]

        #======================================================
        # 5) Set dynamic figure height depending on how many bars are shown
        fig_height = max(5, 0.4 * len(chunk))
        fig, ax = plt.subplots(figsize=(12, fig_height))

        #======================================================
        # 6) Plot a horizontal bar chart with the largest items on top
        bars = ax.barh(paths, sizes, color='skyblue')
        ax.invert_yaxis()

        #======================================================
        # 7) Add labels and a title showing the current page
        ax.set_xlabel("Size")
        ax.set_title(f"Disk Usage ({base_path}) — Page {page + 1}/{total_pages}")

        #======================================================
        # 8) Format the x-axis to show human-readable sizes (e.g., MB, GB)
        ax.xaxis.set_major_formatter(
            ticker.FuncFormatter(lambda x, _: bytes_to_readable(x))
        )

        #======================================================
        # 9) Annotate each bar with the exact size in readable format
        for bar, size in zip(bars, sizes):
            ax.text(
                bar.get_width() + bar.get_width() * 0.01,
                bar.get_y() + bar.get_height() / 2,
                bytes_to_readable(size),
                va='center'
            )

        #======================================================
        # 10) Tweak layout and add subtle grid lines for better readability
        plt.tight_layout()
        plt.grid(axis='x', linestyle='--', alpha=0.6)

        #======================================================
        # 11) Display the chart; if multiple pages, wait for user input
        plt.show(block=False)
        print(f"\nShowing page {page + 1} of {total_pages}.")

        if page < total_pages - 1:
            input("Press Enter to show next page...")
            plt.close(fig)
        else:
            print("Last page. Close the plot window manually to finish.")
