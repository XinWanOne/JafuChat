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

import os
import json

from utilsOllama import get_models

# The typical use is that initial_setup() is called at startup
# If a configuration file is found it loads it, and we are done
# if not it calls select_folder.py to use TK to prompt for a db folder

# These string are the id's used in the json file
INDEX_FOLDER_PATH = "FOLDER_PATH"
INDEX_BASE_DATA = "base_data"
INDEX_BASE_DATA_STORE = "base_data_store"
INDEX_LLM_MODEL = "LLM_MODEL"

# Load the existing JSON file
json_file_path = ""

FOLDER_PATH = "/"

base_data = ""

base_data_store = ""

# Options include various models like "mistral", "dolphin-mixtral", "tinyllama", "llama2", "llava"
LLM_MODEL = "mistral"


def get_model():
    # Environment variables are used to configure the model, embeddings, and storage details dynamically.
    return LLM_MODEL


def get_folder():
    return ""


def get_llm():
    return LLM_MODEL


def get_db(base):
    return os.path.join(base_data_store, base, "_db")


def get_base_dir():
    return base_data


def get_root_dir():
    return base_data_store


# The port the system runs on
def get_port():
    return 8080


def set_model(new_model):
    global LLM_MODEL
    LLM_MODEL = new_model
    save_config()


def get_config_file():
    global json_file_path
    if len(json_file_path) == 0:
        json_file_path = os.path.join(os.path.expanduser('~'), ".jafuChat")
    return json_file_path


def configure():
    config_file_path = get_config_file()
    if os.path.isfile(config_file_path):
        set_config_file(config_file_path)
        return True
    return False


def set_selected_folder(selected_folder):
    if selected_folder.endswith("_db"):
        selected_folder, _ = os.path.split(selected_folder)
    folder_path, folder_name = os.path.split(selected_folder)

    global FOLDER_PATH, base_data, base_data_store
    FOLDER_PATH = selected_folder
    base_data = folder_name
    base_data_store = folder_path
    save_config()


# this is the initial setup
# It gets the ~/.jafuChat file, if it exists
# creates one if it does not exist
def initial_setup(selected_folder):
    # if ~/.jafuChat exist set it and we are done
    global json_file_path
    global INDEX_FOLDER_PATH
    global INDEX_BASE_DATA
    global INDEX_BASE_DATA_STORE
    global INDEX_LLM_MODEL
    config_file_path = get_config_file()

    # get the models available in Ollama
    # pick mistral if found else pick the first one
    model_list = get_models("")
    index = 0
    for m in model_list:
        if m['name'] == 'mistral:latest':
            index = model_list.index(m)
    model = model_list[index]['name']

    if selected_folder.endswith("_db"):
        selected_folder, _ = os.path.split(selected_folder)
        print("remove db")
    folder_path, folder_name = os.path.split(selected_folder)
    print("    FOLDER_PATH:", selected_folder)
    print("      base_data:", folder_name)
    print("base_data_store:", folder_path)
    print("      LLM_MODEL:", LLM_MODEL)

    data = {
        INDEX_FOLDER_PATH: selected_folder,
        INDEX_BASE_DATA: folder_name,
        INDEX_BASE_DATA_STORE: folder_path,
        INDEX_LLM_MODEL: model,
    }

    json_file_path = config_file_path
    save_config_dictionary(data)
    set_config_file(json_file_path)


# Write the config dictionary
def save_config_dictionary(data):
    # Write data to JSON file
    print("json_file_path =", json_file_path)
    with open(json_file_path, "w") as json_file:
        json.dump(data, json_file, indent=4)

    print("Data has been saved to", json_file_path)


# create dictionary and write it
def save_config():
    global json_file_path, FOLDER_PATH, base_data, base_data_store, LLM_MODEL
    global INDEX_FOLDER_PATH
    global INDEX_BASE_DATA
    global INDEX_BASE_DATA_STORE
    global INDEX_LLM_MODEL

    data = {
        INDEX_FOLDER_PATH: FOLDER_PATH,
        INDEX_BASE_DATA: base_data,
        INDEX_BASE_DATA_STORE: base_data_store,
        INDEX_LLM_MODEL: LLM_MODEL,
    }
    save_config_dictionary(data)


def set_config_file(file):
    global json_file_path, FOLDER_PATH, base_data, base_data_store, LLM_MODEL
    global INDEX_FOLDER_PATH
    global INDEX_BASE_DATA
    global INDEX_BASE_DATA_STORE
    global INDEX_LLM_MODEL

    json_file_path = file
    with open(json_file_path, "r") as json_file:
        data = json.load(json_file)
    if INDEX_LLM_MODEL in data:
        LLM_MODEL = data[INDEX_LLM_MODEL]
    else:
        LLM_MODEL = os.environ.get("MODEL", "mistral")

    FOLDER_PATH = data[INDEX_FOLDER_PATH]
    base_data = data[INDEX_BASE_DATA]
    base_data_store = data[INDEX_BASE_DATA_STORE]
