# utils/storage.py (Storage Functions)
import os
import json

def save_data(entry, path="extracted_data/data.json"):
    """
    Appends a resume entry to a local JSON file for persistence.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = []
    if os.path.exists(path):
        with open(path, "r") as f:
            try:
                data = json.load(f)
            except Exception:
                data = []
    data.append(entry)
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

def load_all_data(path="extracted_data/data.json"):
    """
    Loads all stored resume entries.
    """
    if os.path.exists(path):
        with open(path, "r") as f:
            try:
                return json.load(f)
            except Exception:
                return []
    return []
