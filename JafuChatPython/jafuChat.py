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
import sys
import threading
import time

from flask import Flask, request, jsonify, render_template, send_file, send_from_directory
import markdown

from ingest import rebuild_shelf
from jafuGPT import get_answer_from_gpt, setup_llm, get_file_from_db, disconnect
from configuration import get_base_dir, get_port, get_root_dir, set_model, get_know_base, get_llm, get_shelves
import webbrowser
import shutil
from select_folder import initial_setup_with_select, change_folder_path_with_dp_change
from utilsOllama import get_models, ollama_run_if_not

app = Flask(__name__)

conversation_history = []

@app.route('/api/clear_history', methods=['POST'])
def clear_history():
    global conversation_history
    conversation_history = []  # Clear the conversation history
    return jsonify({'status': 'success'})





@app.route('/')
def index():

    if 'settings' in request.args:
        return settings(request.args['settings'])
    links = get_links()
    llm = get_llm()
    return render_template('./index.html', base=get_base_dir(), links=links, model=llm)

@app.route('/favicon.ico')
def favicon():
    print("getting favicon")
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'images/favicon.ico', mimetype='image/vnd.microsoft.icon')

# http calls involving /?settings=
def settings(settings_type):
    if settings_type == "model":
        new_model = request.args['model']
        print("new model = ", new_model)
        set_model(new_model)
    elif settings_type == "dir":
        folder_path_changed = change_folder_path_with_dp_change()  # Assuming the folder path is changed successfully
    elif settings_type == "rebuild":
        shelf = request.args['shelf']
        rebuild_shelf(shelf)  # Assuming the folder path is changed successfully

    llm = get_llm()
    shelves = get_shelves()
    models = get_models(llm)
    return render_template('./settings.html',
                           base=get_base_dir(),
                           root=get_root_dir(),
                           models=models,
                           shelves=shelves,
                           model=llm)

# this and the next one are for :8080/<shelf>
@app.route("/<string:path>")
def doc_str(path):
    links = get_links()
    llm = get_llm()
    return render_template('./index.html', base=path, links=links, model=llm)

# this and the next one are for :8080/<shelf>
@app.route("/<path:path>")
def doc_path(path):
    print("doc_path", path)
    file = get_file_from_db(path)
    return send_file(file, "application/pdf")

# old way of selecting models
@app.route("/#<string:path>")
def select_models(path):
    print("select_models", path)
    links = get_links()
    llm = get_llm()
    return render_template('./index.html', base="demo", links=links, model=llm)

# this is the post query that runs the code
@app.route('/api/query', methods=['POST'])
def process_query():
    global conversation_history
    query = request.json.get('query')
    base = request.json.get('base')

    if query is None:
        return jsonify({'error': 'Query not provided'}), 400

    # Read the system prompt from the file
    system_prompt = None
    prompt_file_name = f"{base}.txt"
    prompt_file_path = os.path.join("prompts", prompt_file_name)

    if os.path.exists(prompt_file_path):
        with open(prompt_file_path, "r") as file:
            system_prompt = file.read()

    # Initialize conversation history with system prompt if it's the first query
    if not conversation_history and system_prompt:
        conversation_history.append(system_prompt)

    # Add the latest query to the conversation history
    conversation_history.append(query)

    # Pass only the latest query to the model while keeping the context
    # latest_context = " ".join([system_prompt, query]) if system_prompt else query
    context = "\n".join(conversation_history)

    # Process the latest query
    answer, docs = get_answer_from_gpt(context, base)
    out = markdown.markdown(answer, extensions=['fenced_code', 'codehilite'])

    # Add the model's response to the conversation history
    conversation_history.append(answer)

    # If necessary, truncate the conversation history to avoid memory issues
    if len(conversation_history) > 20:  # You can adjust this number based on your needs
        conversation_history = conversation_history[-20:]

    if len(docs) > 0:
        out += "<ul>\n"
        for d in docs:
            src = d.metadata["source"]
            number = -1
            if 'page' in d.metadata.keys():
                number = d.metadata["page"]
            out = out + "<li>" + ref_to_string(base, src, number) + "</li>"
        out += "</ul>"

    return jsonify({'answer': out})

def exit_in2sec(error=None):
    time.sleep(3)
    python = sys.executable  # Get the path of the current Python interpreter
    print("restarting ", python)
    print("calling", sys.argv[0])
    os.system(python + "  " + sys.argv[0] + " --noOpen")  # Restart the program

def get_links():
    list = get_know_base()
    links = []
    for dir in list:
        links.append({"href": "./" + dir, "text": dir})
    return links

def ref_to_string(base, file, page_number):
    filename = os.path.basename(file)
    html_name = filename.replace(" ", "%20")
    # Extract the filename

    name = base + "/" + html_name

    # return f'<a href="file:///{html_file}#page={page_number}">{file}({page_number})</a>'
    if page_number == -1:
        return f'<a href="{name}">{file}</a>'
    return f'<a href="{name}#page={page_number+1}">{file}({page_number+1})</a>'

# =============================================


@app.route('/life', methods=['GET', 'POST'])
def change_folder_path_with_dp():
    folder_path_changed = change_folder_path_with_dp_change()  # Assuming the folder path is changed successfully
    if folder_path_changed:
        return "Folder path changed successfully"
    else:
        return "Failed to change folder path"
# =============================================

if __name__ == '__main__':
    # setup_llm("demo")
    if shutil.which("ollama") is None:
        print("ollama not found!")
    ollama_run_if_not()
    initial_setup_with_select()
    if len(sys.argv) > 1 and "--settings" == sys.argv[1]:
        print("opening settings...")
        webbrowser.open_new("http://127.0.0.1:" + str(get_port()) + "/?settings=base")
    else:
        webbrowser.open_new("http://127.0.0.1:" + str(get_port()))
    print("launch browser")
    # app.run(debug=True)
    print("run app infrastructure")
    from waitress import serve

    print("running", sys.argv[0])
    serve(app, host="0.0.0.0", port=get_port())
