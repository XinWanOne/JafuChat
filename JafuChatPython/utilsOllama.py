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


def get_models():
    url = "http://localhost:11434/api/tags"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("Ollama is operational.")
            resp_jason = response.json()
            print(resp_jason['models'])
            models = []
            for m in resp_jason['models']:
                models.append({'name': m['name'], 'size': m['size']})
            return models
        else:
            print("Ollama responded, but there might be an issue:", response.status_code)
            print("> :", response)
    except requests.exceptions.ConnectionError:
        print("Failed to connect to Ollama. It might not be running.")



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
    if check_if_ollama_is_running():
        print("Ollama process is running.")
        getListOfModels()
    else:
        print("Ollama process is not running.")



