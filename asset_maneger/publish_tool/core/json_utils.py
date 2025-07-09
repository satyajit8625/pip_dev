import json
import logging
import os

def save_json(path: str, file_name: str, data: dict) -> bool:
    """
    Saves a dictionary to a file in JSON format.

    Args:
        path (str): The directory path where the file will be saved.
        file_name (str): The name of the output file (including .json extension).
        data (dict): The dictionary to save.

    Returns:
        bool: True if the file was saved successfully, False otherwise.
    """
    try:
        if not os.path.exists(path):
            os.makedirs(path)
            
        file_path = os.path.join(path, file_name)
        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        logging.error(f"[JsonUtils] Failed to save JSON to '{file_path}': {e}")
        return False

def load_json(path: str, file_name: str) -> dict:
    """
    Loads a dictionary from a file in JSON format.

    Args:
        path (str): The directory path where the file is located.
        file_name (str): The name of the input file (including .json extension).

    Returns:
        dict: The loaded dictionary, or None if an error occurs.
    """
    file_path = os.path.join(path, file_name)
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        
        return None
    except json.JSONDecodeError:
        logging.error(f"[JsonUtils] Failed to decode JSON from '{file_path}'")
        return None
    except Exception as e:
        logging.error(f"[JsonUtils] Failed to load JSON from '{file_path}': {e}")
        return None

def update_json(path: str, file_name: str, new_data: dict) -> bool:
    """
    Updates an existing JSON file with new data. If the file doesn't exist,
    it will be created.

    Args:
        path (str): The directory path of the JSON file.
        file_name (str): The name of the JSON file.
        new_data (dict): The dictionary containing new data to be merged.

    Returns:
        bool: True if the file was updated successfully, False otherwise.
    """
    data = load_json(path, file_name)
    if data is None:
        data = {}

    data.update(new_data)

    return save_json(path, file_name, data)

def update_publish_history(path: str, file_name: str, new_entry: dict) -> bool:
    """
    Updates a JSON file by appending a new entry to a 'publish_history' list.
    If the file doesn't exist, it creates it with the initial asset info.

    Args:
        path (str): The directory path of the JSON file.
        file_name (str): The name of the JSON file (e.g., 'metadata.json').
        new_entry (dict): The new dictionary to append to the history.

    Returns:
        bool: True if the file was updated successfully, False otherwise.
    """
    data = load_json(path, file_name)
    
    if data is None:
        # If file doesn't exist, create the base structure
        data = {
            "asset_name": new_entry.get("asset_name"),
            "asset_type": new_entry.get("asset_type"),
            "publish_history": []
        }

    # Ensure publish_history list exists
    if "publish_history" not in data:
        data["publish_history"] = []
        
    data["publish_history"].append(new_entry)

    return save_json(path, file_name, data)