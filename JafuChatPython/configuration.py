import os

FOLDER_PATH = "C:/Users/white/Documents/GitHub/chatJafu/exmples/demo"

base_data = "demo"

base_data_store = "C:/Users/white/Documents/GitHub/chatJafu/exmples/"

# Options include various models like "mistral", "dolphin-mixtral", "tinyllama", "llama2", "llava"
LLM_MODEL = "mistral"


def get_model():
    # Environment variables are used to configure the model, embeddings, and storage details dynamically.
    return model


def get_folder():
    return ""


def get_llm():
    return LLM_MODEL


def get_db(base):
    return base_data_store + base + "/_db"


def get_base_dir():
    return base_data


def get_root_dir():
    return base_data_store


def get_port():
    return 8080


model = os.environ.get("MODEL", LLM_MODEL)
