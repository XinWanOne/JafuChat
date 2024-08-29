__copyright__ = """

    Copyright 2024 Jason Hofordf

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

import gc

# Import necessary modules from langchain and other libraries

from langchain.chains import RetrievalQA
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.llms import Ollama
from nltk import word_tokenize

from configuration import get_model, get_db, get_root_dir
import os
import time
from rank_bm25 import BM25Okapi
import nltk
import json
import os
import ssl
from nltk.corpus import stopwords

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# Ensure NLTK data is downloaded
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')



# Load the configuration from config.json
config_file_path = os.path.join(os.path.dirname(__file__), 'embeddingconfig.json')
with open(config_file_path, 'r') as config_file:
    config = json.load(config_file)

# # Access the configuration values
persist_directory = config.get('persist_directory', 'db')
embeddings_model_name = config.get('embeddings_model_name', 'all-MiniLM-L6-v2')
chunk_size = config.get('chunk_size', 500)
chunk_overlap = config.get('chunk_overlap', 50)


# Define the embeddings model to use for creating semantic embeddings of the texts.
# embeddings_model_name = os.environ.get("EMBEDDINGS_MODEL_NAME", "all-MiniLM-L6-v2")
target_source_chunks = int(os.environ.get('TARGET_SOURCE_CHUNKS', 6))

# Debug flag for printing additional information
debug = False

def preprocess_text(text):
    tokens = word_tokenize(text.lower())
    tokens = [word for word in tokens if word.isalnum()]  # Remove punctuation
    tokens = [word for word in tokens if word not in stopwords.words('english')]  # Remove stopwords
    return tokens
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


def disconnect():
    global llm
    global retriever
    object_methods = [method_name for method_name in dir(retriever)
                      if callable(getattr(retriever, method_name))]
    print(object_methods)
    retriever = None
    llm = None
    gc.collect()



def get_answer_from_gpt(context, base):
    global llm, retriever

    # Initialize the embeddings using HuggingFace's models
    embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-m3")

    # Set up the Chroma vector store with the specified directory and embedding function
    db = Chroma(persist_directory=get_db(base), embedding_function=embeddings)

    # Use the Chroma DB as a retriever with specified search parameters
    retriever = db.as_retriever(search_kwargs={"k": target_source_chunks})

    # Retrieve documents using the retriever
    initial_docs = retriever.get_relevant_documents(context)

    if not initial_docs:
        print("No documents retrieved.")

        # If no documents are retrieved, just use the context with the LLM
        llm = Ollama(model=get_model(), callbacks=[])
        response = llm(context)  # Pass the context as a plain string
        return response, []  # Return the response directly

    # Check the content of the retrieved documents
    print("\nDocument Contents for BM25 Processing:")
    for i, doc in enumerate(initial_docs):
        print(f"Document {i + 1} Content: {doc.page_content[:200]}...")  # Print the first 200 characters

    # Extract text for BM25 processing
    corpus = [preprocess_text(doc.page_content) for doc in initial_docs]

    # Check the query content
    print(f"\nQuery for BM25: {context}")

    # Initialize BM25
    bm25 = BM25Okapi(corpus)
    # Rerank documents using BM25
    scores = bm25.get_scores(context.split())

    # Print scores for debugging
    print("\nBM25 Scores for Retrieved Documents:")
    for i, score in enumerate(scores):
        print(f"Document {i + 1}: Score = {score}")

    # Combine scores with documents and sort them by score
    ranked_docs = [doc for _, doc in sorted(zip(scores, initial_docs), key=lambda x: x[0], reverse=True)]

    # Print the order of documents after reranking
    print("\nDocuments after BM25 Reranking:")
    for i, doc in enumerate(ranked_docs):
        print(f"Document {i + 1}: {doc.metadata.get('source', 'No Source')}")

    # Initialize the large language model (LLM) without any callbacks
    llm = Ollama(model=get_model(), callbacks=[])

    # Create the RetrievalQA chain
    qa = RetrievalQA.from_chain_type(
        llm=llm, chain_type="stuff", retriever=retriever, return_source_documents=True
    )

    # Use the top-ranked documents as input to the generative model
    response = qa({"query": context, "documents": ranked_docs})

    # Extract the answer and source documents
    answer = response["result"]
    docs = response["source_documents"]

    return answer, docs


    # without reranking code
    # global llm, retriever
    # # Initialize the embeddings using HuggingFace's models
    # embeddings = HuggingFaceEmbeddings(model_name=embeddings_model_name)
    #
    # # Set up the Chroma vector store with the specified directory and embedding function
    # db = Chroma(persist_directory=get_db(base), embedding_function=embeddings)
    #
    # # Use the Chroma DB as a retriever with specified search parameters
    # retriever = db.as_retriever(search_kwargs={"k": target_source_chunks})
    #
    # # Initialize the large language model (LLM) without any callbacks
    # llm = Ollama(model=get_model(), callbacks=[])
    #
    # # # Include the system prompt as part of the context
    # # if system_prompt and not conversation_history:
    # #     context = f"{system_prompt}\n{context}"
    #
    # # Create the RetrievalQA chain
    # qa = RetrievalQA.from_chain_type(
    #     llm=llm, chain_type="stuff", retriever=retriever, return_source_documents=True
    # )
    #
    # # Get the answer from the chain
    # response = qa({"query": context})
    #
    # # Extract the answer and source documents
    # answer = response["result"]
    # docs = response["source_documents"]
    #
    # return answer, docs






# def translate_to_chinese(text):
#     import ollama
#     message = [{'role': 'user', 'content': '"'+text+'"  convert to Chinese do not output anything else'}]
#     response = ollama.chat(model=get_model(),messages=message)
#     return response['message']['content']


def get_file_from_db(name):
    path = get_root_dir() + "/" + name
    print("opening", path)
    return path
    # return open(path, 'rb').read()


# Example usage, if this script is run directly
if __name__ == '__main__':
    run_private_gpt("C:/chatWithJafu", 'C:/chatWithJafu/_db')
