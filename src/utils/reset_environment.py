import shutil
import os
from pathlib import Path

def reset_data_folder():
    data_folder = Path(__file__).parent.parent.parent / "data"
    print(f"Resetting data folder at: {data_folder}")
    
    if data_folder.exists() and data_folder.is_dir():
        shutil.rmtree(data_folder)
        print(f"Cartella '{data_folder}' cancellata.")
    else:
        print(f"La cartella '{data_folder}' non esiste.")
    
    
# Esempio di utilizzo:
reset_data_folder()