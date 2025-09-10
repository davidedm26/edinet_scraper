import shutil
import os
from pathlib import Path

def reset_data_folder():
    data_folder = Path(__file__).parent.parent.parent / "data"
    print(f"Resetting data folder at: {data_folder}")
    if data_folder.exists() and data_folder.is_dir():
        for item in data_folder.iterdir():
            if item.is_file() or item.is_symlink():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)
        print(f"Contents of the folder '{data_folder}' have been deleted.")
    else:
        print(f"The folder '{data_folder}' does not exist.")

# Example usage:
# reset_data_folder()
