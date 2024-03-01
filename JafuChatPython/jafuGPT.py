# Import necessary modules from langchain and other libraries
import io

from langchain.chains import RetrievalQA
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.llms import Ollama
import os
import time

# Options include various models like "mistral", "dolphin-mixtral", "tinyllama", "llama2", "llava"
LLM_MODEL = "mistral"

# Environment variables are used to configure the model, embeddings, and storage details dynamically.
model = os.environ.get("MODEL", LLM_MODEL)

# Define the embeddings model to use for creating semantic embeddings of the texts.
embeddings_model_name = os.environ.get("EMBEDDINGS_MODEL_NAME", "all-MiniLM-L6-v2")
target_source_chunks = int(os.environ.get('TARGET_SOURCE_CHUNKS', 4))

# Debug flag for printing additional information
debug = False


def run_privateGPT(source_directory,persist_directory):
    # Initialize the embeddings using HuggingFace's models
    embeddings = HuggingFaceEmbeddings(model_name=embeddings_model_name)

    # Set up the Chroma vector store with the specified directory and embedding function
    db = Chroma(persist_directory=persist_directory, embedding_function=embeddings)

    # Use the Chroma DB as a retriever with specified search parameters
    retriever = db.as_retriever(search_kwargs={"k": target_source_chunks})

    # Initialize the large language model (LLM) without any callbacks
    llm = Ollama(model=model, callbacks=[])

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
            print(">",document.metadata["source"],"pg:",document.metadata["page"])

        # If in debug mode, print the source documents that were used to generate the answer
        if debug:
            for document in docs:
                print("\n> " + document.metadata["source"] + ":")
                print(document.page_content)


llm = None
retriever = None
base_data = "demo"

base_data_store = "C:/Users/white/Documents/GitHub/chatJafu/exmples/"


def get_db(base):
    return base_data_store+base+"/_db"


def setup_llm(base):
    global llm
    global retriever
    embeddings = HuggingFaceEmbeddings(model_name=embeddings_model_name)

    db = Chroma(persist_directory=get_db(base), embedding_function=embeddings)

    retriever = db.as_retriever(search_kwargs={"k": target_source_chunks})
    # activate/deactivate the streaming StdOut callback for LLMs

    llm = Ollama(model=model, callbacks=[])


def get_answer_from_gpt(query, base):
    global llm, retriever
    # Initialize the embeddings using HuggingFace's models
    embeddings = HuggingFaceEmbeddings(model_name=embeddings_model_name)

    # Set up the Chroma vector store with the specified directory and embedding function
    db = Chroma(persist_directory=get_db(base), embedding_function=embeddings)

    # Use the Chroma DB as a retriever with specified search parameters
    retriever = db.as_retriever(search_kwargs={"k": target_source_chunks})

    # Initialize the large language model (LLM) without any callbacks
    llm = Ollama(model=model, callbacks=[])

    qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever, return_source_documents=True)

    # Get the answer from the chain
    res = qa(query)
    answer = res['result']
    docs = res['source_documents']
    print(res.keys())
    return answer, docs


def get_base_dir():
    return base_data


def get_file_from_db(name):
    path = base_data_store+"/"+name
    print("opening",path)
    return path
    # return open(path, 'rb').read()


def get_llm():
    return LLM_MODEL


def get_know_base():
    return next(os.walk(base_data_store))[1]


# Example usage, if this script is run directly
if __name__ == '__main__':
    run_privateGPT("C:/chatWithJafu",  'C:/chatWithJafu/_db')


