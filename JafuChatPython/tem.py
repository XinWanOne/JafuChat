import json
from utilsOllama import get_models

"""
To DO: Need to delete this file in the final version
current propose is to show how to save data as json file
"""

data = {
    "FOLDER_PATH": "default_folder",
    "base_data": "demo",
    "base_data_store": "default_folder",
    "LLM_MODEL": get_models("")[0]['name']
}

# Specify the path for the JSON file
json_file_path = "data.json"

# Write data to JSON file
with open(json_file_path, "w") as json_file:
    json.dump(data, json_file, indent=4)

print("Data has been saved to", json_file_path)
