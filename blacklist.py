import json

def load_blacklist(file_path="json/blacklist.json"):
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error Loading Blacklist: {e}")
        return []
