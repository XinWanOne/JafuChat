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

from flask import Flask, request, jsonify, render_template, send_file
from jafuGPT import get_answer_from_gpt, setup_llm, get_file_from_db, get_know_base, get_llm
from configuration import get_base_dir, get_port, get_root_dir, set_model
import webbrowser
import shutil
from select_folder import initial_setup_with_select, change_folder_path_with_dp_change
from utilsOllama import get_models, ollama_run_if_not

app = Flask(__name__)


# main html access typically renders index.html
@app.route('/')
def index():
    if 'settings' in request.args:
        print("index", request.args['settings'])
        return settings(request.args['settings'])
    links = get_links()
    llm = get_llm()
    return render_template('./index.html', base=get_base_dir(), links=links, model=llm)


# http calls involving /?settings=
def settings(type):
    if type == "model":
        new_model = request.args['model']
        print("new model = ", new_model)
        set_model(new_model)
    if type == "dir":
        folder_path_changed = change_folder_path_with_dp_change()  # Assuming the folder path is changed successfully

    links = get_links()
    llm = get_llm()
    models = get_models(llm)
    return render_template('./settings.html',
                           base=get_base_dir(),
                           root=get_root_dir(),
                           models=models,
                           links=links,
                           model=llm)


# this and the next one are for :8080/<shelf>
@app.route("/<string:path>")
def doc_str(path):
    print("doc_str", path)
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
    print("query")
    query = request.json.get('query')
    base = request.json.get('base')
    print("base:", base)
    if query is None:
        return jsonify({'error': 'Query not provided'}), 400

    # Process the query using your Python script
    answer, docs = get_answer_from_gpt(query, base)
    out = answer
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


def get_links():
    list = get_know_base()
    links = []
    for dir in list:
        links.append({"href": "./" + dir, "text": dir})
    return links


def ref_to_string(base, file, page_number):
    html_file = file.replace(" ", "%20")
    name = base + "/" + html_file[html_file.rindex('\\') + 1:]
    # return f'<a href="file:///{html_file}#page={page_number}">{file}({page_number})</a>'
    if page_number == -1:
        return f'<a href="{name}">{file}</a>'
    return f'<a href="{name}#page={page_number}">{file}({page_number})</a>'


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
    webbrowser.open_new("http://127.0.0.1:" + str(get_port()))
    print("launch browser")
    # app.run(debug=True)
    print("run app infrastructure")
    from waitress import serve

    serve(app, host="0.0.0.0", port=get_port())
