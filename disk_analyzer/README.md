# OS Project: Disk Space Analyzer

This repository is for a **Disk Space Analyzer** project of **ITCS225: Principles of Operating System** by **Apes Together Strong** group (section 2).

<br>

## 🔍 Table of Contents

- [About](#about)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Examples](#examples)
- [Contributing](#contributing)
- [License](#license)

<br>

## 📖 About

Many users struggle to identify large or unnecessary files, leading to storage inefficiencies. A Disk Space Analyzer provides a clear overview of file distribution, helping users decisively free up space effectively.

<br>

## ✨ Features

- Disk Usage Analysis: Analyzes disk space usage across all available drives or selected directories while also provides detailed information about the disk's total, used, and free space.
- Recursive Directory Scanning: Recursively scans directories and sum up the sizes of all files and folders.
- Detailed File Size Reporting: Sizes are presented in human-readable formats (e.g., KB, MB, GB) for easy understanding.
- Visualization: Display the results in paginated format to handle large directories, making it easier to navigate through results, which will also be visualized in bar charts, with horizontal bars representing file sizes.
- Benchmark Logging: logs detailed performance benchmarks and logs are saved in a CSV file:
  - Time taken to scan the directory
  - Total number of files processed
  - Aggregate size of files processed
  - CPU usage
  - memory usage
  - disk I/O statistics
  - process-specific I/O
- Efficient Resource Management: Optimized algorithms to minimize resource usage during the scan.
- Modular Design: Designed with a modular structure where utilities are separated into different modules for easier maintenance and extensibility.

<br>

## ⚙️ Installation

(Delete this: 
Step-by-step instructions to get the project running locally (install).
Do this after finish the code?)

```Installation
# Clone the repository
git clone https://github.com/Waraaaa/apes-goldf-predict.git
cd apes-goldf-predict

# Install required packages (if we have one, put the name in requirement.txt)
pip install -r requirement.txt
```

<br>

## 🚀 Usage

(Delete this: How to run the program)

```
python main.py
```

<br>

## 🗂️ Project Structure

```Structure
disk_analyzer/
│
├── versions/              
│   ├── __init__.py
│   ├── base_ver.py            # Default version
│   ├── threaded_ver.py        # Version with multithreading
│   └── async_ver.py           # Version using asyncio
│
├── utils/
│   ├── __init__.py
│   ├── analyzer_helpers.py   # Common helper functions e.g. get_size(), bytes_to_readable()
│   ├── plotting.py           # For plotting bar charts
│   └── benchmark.py          # For logging benchmarks to CSV
│
├── main.py                # Main entry, lets user select which version to run
├── requirements.txt       # Collect all python packages that is required
└── README.md
```
- `__init__.py`: Marks the directory as a Python package.
- `versions/`: Contains all versions of the disk analyzer program (e.g., base, threaded, async).
- `utils/`: Contains reusable utility modules shared across different versions.

<br>

## 🧪 Examples

(Delete this: output examples, maybe screenshots)

<br>

## 🤝 Contributing

Apes Together Strong (section 2)
- 6688001 Pattareeya Achaiyaphoom
- 6688013 Korawit Chantavilaiying
- 6688021 Apinut Cotivongsa
- 6688032 Nipada Jadjaidee
- 6688157 Woraphol Meakapat

<br>

## 📄 License

This project is for academic purposes only.


