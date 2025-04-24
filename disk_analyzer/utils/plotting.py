def plot(data, base_path, page_size=20):
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
