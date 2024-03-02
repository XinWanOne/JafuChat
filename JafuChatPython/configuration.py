import os
import json

# Load the existing JSON file
json_file_path = "data.json"
with open(json_file_path, "r") as json_file:
    data = json.load(json_file)

FOLDER_PATH = data['FOLDER_PATH']

base_data = data['base_data']

base_data_store = data['base_data_store']

# Options include various models like "mistral", "dolphin-mixtral", "tinyllama", "llama2", "llava"
LLM_MODEL = data['LLM_MODEL']


def get_model():
    # Environment variables are used to configure the model, embeddings, and storage details dynamically.
    return model


def get_folder():
    return ""


def get_llm():
    return LLM_MODEL


def get_db(base):
    print(os.path.join(base_data_store,base,"_db"))
    return os.path.join(base_data_store,base,"_db")


def get_base_dir():
    return base_data


def get_root_dir():
    return base_data_store


def get_port():
    return 8080


model = os.environ.get("MODEL", LLM_MODEL)
