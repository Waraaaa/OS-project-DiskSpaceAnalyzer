# OS Project: Disk Space Analyzer

For OS project.

<br>

## 1. DSA with No Performance Enhancement (Default)

aaaaaa

<br>

### 1.1 Import Important Modules

```
import subprocess
import sys
import os
```
They are
+ subprocess - for
+ sys - for
+ os - for

<br>

### 1.2 Auto-install Required Libraries

```
def install_requirements():
    try:
        # Try import necessary packages
        import psutil
        import matplotlib.pyplot as plt
        import pandas
    except ImportError:
        # If any import fails -> install from requirements.txt
        requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_path])

install_requirements()  # Run the installation def above.
```
Auto-install required libraries from requirements.txt if they're not already installed.

<br>

### 1.3 Imports

```
import os
import shutil
import psutil
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import time
import csv
from datetime import datetime
```
For import explain each import.

<br>

### 1.4 Byte Size Conversion

```
def bytes_to_readable(size):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} PB"
```
Converts byte size into --> e.g., KB, MB, GB.

<br>

### 1.5 System Drives Listing

```
def list_drives():
    partitions = psutil.disk_partitions(all=False)
    return [p.device for p in partitions]
```
List all drives in the system (like C:\, D:\).

<br>

### 1.6 ?

```

```

<br>

### 1.7 ?

```

```

<br>

### 1.8 ?

```

```

<br>

### 1.9 ?

```

```

<br>

### 1.10 ?

```

```

<br>

### 1.11 ?

```

```

<br>

### 1.12 ?

```

```

<br>

### 1.13 ?

```

```


