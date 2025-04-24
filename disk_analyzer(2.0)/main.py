import asyncio
import psutil
import install
from disk_analyzer import analyzer as base_analyzer
from disk_analyzer_optimize import analyzer as optimized_analyzer

#======================================================
# List all mounted disk drives
def list_drives():
    partitions = psutil.disk_partitions(all=False)
    return [p.device for p in partitions]

#======================================================
# If only one drive exists, auto-select it; otherwise ask user
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

#======================================================
# Handle user input for drive selection when multiple drives exist
def input_case(drives):
    print("This program found more than 1 drive.")
    print("Please select the drive. Type the number: (\"exit\" to end)")
    while True:
        number = input()
        if number == "exit":
            exit()
        if number.isdigit() and 1 <= int(number) <= len(drives):
            return drives[int(number) - 1]
        else:
            print("Invalid drive. Try again.")

#======================================================
# Main async function to run the analyzer
async def main():
    restart = False
    drives = list_drives()

    # Display all available drives
    for i, d in enumerate(drives):
        print(f"{i + 1}: {d}")
    
    # Choose drive
    path = "/" if len(drives) == 1 else input_case(drives)

    # Select analyzer version
    print("Select analyzer version:")
    print("1) Base (single-threaded)")
    print("2) Optimized (Threaded & Asyncio)")
    choice = input("> ")
    
    # Run selected analyzer
    if choice == "1":
        restart = base_analyzer.analyzer(path)  # Synchronous call
    elif choice == "2":
        restart = await optimized_analyzer.analyzer(path)  # Asynchronous call
    else:
        print("Invalid selection")
    
    # Optionally restart scan
    if restart:
        await main()

#======================================================
# Entry point
if __name__ == "__main__":
    asyncio.run(main())
