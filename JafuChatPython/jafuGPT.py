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

# Import necessary modules from langchain and other libraries
import io

from langchain.chains import RetrievalQA
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.llms import Ollama
from configuration import get_llm, get_model, get_db, get_root_dir

import os
import time

# Define the embeddings model to use for creating semantic embeddings of the texts.
embeddings_model_name = os.environ.get("EMBEDDINGS_MODEL_NAME", "all-MiniLM-L6-v2")
target_source_chunks = int(os.environ.get('TARGET_SOURCE_CHUNKS', 4))

# Debug flag for printing additional information
debug = False


def run_private_gpt(source_directory, persist_directory):
    # Initialize the embeddings using HuggingFace's models
    embeddings = HuggingFaceEmbeddings(model_name=embeddings_model_name)

    # Set up the Chroma vector store with the specified directory and embedding function
    db = Chroma(persist_directory=persist_directory, embedding_function=embeddings)

    # Use the Chroma DB as a retriever with specified search parameters
    retriever = db.as_retriever(search_kwargs={"k": target_source_chunks})

    # Initialize the large language model (LLM) without any callbacks
    llm = Ollama(model=get_model(), callbacks=[])

    # Set up the RetrievalQA chain with the LLM, retriever, and specify to return source documents
    qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever, return_source_documents=True)

    # Interactive loop for handling user queries
    while True:
        query = input()
        if query == "exit":
            break
        if query == "quit":
            break
        if query.strip() == "":
            continue

        # Process the query using the retrieval-augmented QA model
        start = time.time()
        res = qa(query)
        answer, docs = res['result'], res['source_documents']
        print(">>", res.keys())
        end = time.time()

        # Output the answer to the user's query
        print()
        print('______________________________________')
        print(answer)
        print('______________________________________')
        for document in docs:
            print(">", document.metadata["source"], "pg:", document.metadata["page"])

        # If in debug mode, print the source documents that were used to generate the answer
        if debug:
            for document in docs:
                print("\n> " + document.metadata["source"] + ":")
                print(document.page_content)


llm = None
retriever = None


def setup_llm(base):
    global llm
    global retriever
    embeddings = HuggingFaceEmbeddings(model_name=embeddings_model_name)

    db = Chroma(persist_directory=get_db(base), embedding_function=embeddings)

    retriever = db.as_retriever(search_kwargs={"k": target_source_chunks})
    # activate/deactivate the streaming StdOut callback for LLMs

    llm = Ollama(model=get_model(), callbacks=[])


def get_answer_from_gpt(query, base):
    global llm, retriever
    # Initialize the embeddings using HuggingFace's models
    embeddings = HuggingFaceEmbeddings(model_name=embeddings_model_name)

    # Set up the Chroma vector store with the specified directory and embedding function
    db = Chroma(persist_directory=get_db(base), embedding_function=embeddings)

    # Use the Chroma DB as a retriever with specified search parameters
    retriever = db.as_retriever(search_kwargs={"k": target_source_chunks})

    # Initialize the large language model (LLM) without any callbacks
    llm = Ollama(model=get_model(), callbacks=[])

    qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever, return_source_documents=True)

    # Get the answer from the chain
    res = qa(query)
    answer = res['result']
    docs = res['source_documents']
    print(res.keys())
    return answer, docs


def get_file_from_db(name):
    path = get_root_dir() + "/" + name
    print("opening", path)
    return path
    # return open(path, 'rb').read()


def get_know_base():
    return next(os.walk(get_root_dir()))[1]


# Example usage, if this script is run directly
if __name__ == '__main__':
    run_private_gpt("C:/chatWithJafu", 'C:/chatWithJafu/_db')
