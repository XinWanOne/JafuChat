__copyright__ = """

    Copyright 2024 Jason Hoford

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

"""
__license__ = "Apache 2.0"

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
