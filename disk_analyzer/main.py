import sys
from versions import base_ver, threaded_ver, async_ver
from utils.analyzer_helpers import list_drives

def select_drive():
    drives = list_drives()
    if len(drives) == 1:
        return drives[0]
    for i, d in enumerate(drives, 1):
        print(f"{i}: {d}")
    while True:
        choice = input("Select drive: ")
        if choice.isdigit() and 1 <= int(choice) <= len(drives):
            return drives[int(choice) - 1]

def main():
    print("Select analyzer version:")
    print("1) Base (single-threaded)")
    print("2) Threaded & Asyncio")
    choice = input("> ")
    path = select_drive()
    if choice == "1":
        base_ver.analyze(path)
    elif choice == "2":
        threaded_ver.analyze(path)
    elif choice == "3":
        async_ver.run(path)
    else:
        print("Invalid selection")

if __name__ == "__main__":
    main()
