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

# from langchain.llms import Ollama
#
#
#
# LLM_MODEL = "mistral"
# model = os.environ.get("MODEL", LLM_MODEL)
# llm = Ollama(model=model, callbacks=[])
#
#
import requests
import psutil
import subprocess
import shutil

def check_if_ollama_is_running():
    for proc in psutil.process_iter(['name']):
        if "ollama" in proc.info['name'].lower():
            return True
    return False

def getListOfModels():
    url = "http://localhost:11434/api/tags"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("Ollama is operational.")
            resp_jason = response.json()
            print(resp_jason['models'])
            for m in resp_jason['models']:
                print(m['name'], int((m['size']/(1024*1024)))/1024)
            return resp_jason['models']
        else:
            print("Ollama responded, but there might be an issue:", response.status_code)
            print("> :", response)
    except requests.exceptions.ConnectionError:
        print("Failed to connect to Ollama. It might not be running.")


def format_size(size):
    if size > (1024*1024*1024):
        return "{:.1f}GB".format(size/(1024*1024*1024))
    return "{:.1f}MB".format(size/(1024*1024))


def get_models(current):
    url = "http://localhost:11434/api/tags"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("Ollama is operational.")
            resp_jason = response.json()
            print(resp_jason['models'])
            models = []
            for m in resp_jason['models']:

                    models.append({'name': m['name'],
                                   'size': format_size(m['size']),
                                   'selected': (m['name'] == current)
                                   })
            return models
        else:
            print("Ollama responded, but there might be an issue:", response.status_code)
            print("> :", response)
    except requests.exceptions.ConnectionError:
        print("Failed to connect to Ollama. It might not be running.")


# if not running, run ollama
def ollama_run_if_not():
    if check_if_ollama_is_running():
        print("ollama was running")
        return True
    print("running ollama serve...")
    try:
        subprocess.Popen(["ollama", "serve"])
    except subprocess.CalledProcessError:
        print("ollama may not be installed")

def test_ollama_endpoint():
    url = "http://localhost:11434/api/tags"  # Example URL, adjust based on your setup
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("Ollama is operational.")
            print("> :", response.json())
        else:
            print("Ollama responded, but there might be an issue:", response.status_code)
            print("> :", response)
    except requests.exceptions.ConnectionError:
        print("Failed to connect to Ollama. It might not be running.")

# Assuming you have already checked that Ollama is installed


if __name__ == '__main__':
    print('ollama > ', shutil.which("ollama"))
    # try:
    #     subprocess.Popen(["ollamass", "serve"])
    # except subprocess.CalledProcessError:
    #     print("fail")
    #     exit(0)
    # print("just went on")

    ollama_run_if_not()
    if check_if_ollama_is_running():
        print("Ollama process is running.")
        getListOfModels()
    else:
        print("Ollama process is not running.")



