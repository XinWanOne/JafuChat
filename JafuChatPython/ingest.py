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

import shutil

from configuration import get_root_dir, get_db

"""Script Overview At its core, the script is designed to automate the conversion of raw documents from various
formats into a structured, queryable format. This process encompasses several steps: identifying and loading
documents, extracting and preprocessing the text, generating embeddings, and storing these embeddings in a vector
store for efficient search and retrieval.

Environment Set up The script begins by setting up essential directories and configurations through environment
variables. These include paths for source documents and the persistence directory for the vector store, as well as
settings for the embeddings model and text chunking parameters.

Loader Mapping and Document Loading The script employs a LOADER_MAPPING dictionary to map file extensions to their
respective document loaders, enabling the dynamic handling of multiple document formats. This mapping facilitates the
loading process, where documents are identified based on their extensions and processed using the appropriate loaders.

load_single_document The load_single_document function is responsible for loading a document given its file path. It
retrieves the correct loader from LOADER_MAPPING based on the file extension and invokes the loader to extract the
document's content.

load_documents The load_documents function iterates over all files in the source directory, filtering out any
specified to be ignored. It leverages Python's multiprocessing capabilities to parallelize the loading of documents,
significantly improving efficiency for large datasets.

Document Processing and Text Splitting After loading, documents are processed and split into manageable chunks by the
process_documents function. This step is crucial for preparing the text for embedding generation, ensuring each piece
is of a suitable size for processing. The function uses a RecursiveCharacterTextSplitter from LangChain, highlighting
the script's use of advanced text processing techniques to handle large and complex documents.

Vector Store Interaction does_vectorstore_exist Before ingesting new data, the script checks if a vector store
already exists using the does_vectorstore_exist function. This function ensures that the script can seamlessly
integrate with existing data repositories, either by updating them with new documents or creating a new store if
necessary.

ingest_files The main ingestion logic resides within the ingest_files function. It first initializes the embeddings
using a model specified by the environment variables. Depending on whether a vector store already exists,
it either appends new documents to the existing store or creates a new one. This function demonstrates the script's
capability to generate embeddings and efficiently store them, enabling advanced search and retrieval functionalities.

Execution Flow The script culminates in the if __name__ == "__main__": block, where the ingest_files function is
called to kick off the entire document ingestion and indexing process. This entry point ensures that the script can
operate both as a standalone tool and as part of a larger data processing pipeline, offering flexibility and
scalability in handling document-based information retrieval tasks.
"""
import os
import glob
from typing import List
from multiprocessing import Pool
from tqdm import tqdm

# Import LangChain libraries for document loading, text splitting, embeddings, and vector storage
from langchain_community.document_loaders import (
    CSVLoader, EverNoteLoader, PyMuPDFLoader, TextLoader,
    UnstructuredEmailLoader, UnstructuredEPubLoader, UnstructuredHTMLLoader,
    UnstructuredMarkdownLoader, UnstructuredODTLoader, UnstructuredPowerPointLoader,
    UnstructuredWordDocumentLoader,
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.docstore.document import Document
from constants import CHROMA_SETTINGS

# Load essential environment variables for configuration
persist_directory = os.environ.get('PERSIST_DIRECTORY', 'db')
embeddings_model_name = os.environ.get('EMBEDDINGS_MODEL_NAME', 'all-MiniLM-L6-v2')
chunk_size = 500
chunk_overlap = 50

# Mapping of file extensions to their respective document loaders
LOADER_MAPPING = {
    ".csv": (CSVLoader, {}),
    ".default_folder": (UnstructuredWordDocumentLoader, {}),
    ".docx": (UnstructuredWordDocumentLoader, {}),
    ".enex": (EverNoteLoader, {}),
    ".epub": (UnstructuredEPubLoader, {}),
    ".html": (UnstructuredHTMLLoader, {}),
    ".md": (UnstructuredMarkdownLoader, {}),
    ".odt": (UnstructuredODTLoader, {}),
    ".pdf": (PyMuPDFLoader, {}),
    ".ppt": (UnstructuredPowerPointLoader, {}),
    ".pptx": (UnstructuredPowerPointLoader, {}),
    ".txt": (TextLoader, {"encoding": "utf8"}),
}


def load_single_document(file_path: str) -> List[Document]:
    """Loads a single document based on its file path."""
    ext = os.path.splitext(file_path)[1]
    if ext in LOADER_MAPPING:
        loader_class, loader_args = LOADER_MAPPING[ext]
        loader = loader_class(file_path, **loader_args)
        return loader.load()
    raise ValueError(f"Unsupported file extension '{ext}'")


def load_documents(source_dir: str, ignored_files: List[str] = []) -> List[Document]:
    """Loads documents from the source directory, excluding any specified ignored files."""
    # all_files = [glob.glob(os.path.join(source_dir, f"**/*{ext}"), recursive=True) for ext in LOADER_MAPPING]
    all_files = [glob.glob(os.path.join(source_dir, f"**/*{ext}"), recursive=True) for ext in LOADER_MAPPING]
    filtered_files = [file for sublist in all_files for file in sublist if file not in ignored_files]
    print(source_dir, len(all_files), " files", all_files)
    with Pool(processes=os.cpu_count()) as pool:
        results = []
        with tqdm(total=len(filtered_files), desc='Loading documents', ncols=80) as pbar:
            for docs in pool.imap_unordered(load_single_document, filtered_files):
                results.extend(docs)
                pbar.update()
    return results


def process_documents(ignored_files: List[str] = [], source_directory=None) -> List[Document]:
    """Processes documents by loading and splitting them into manageable chunks."""
    print(f"Loading documents from {source_directory}")
    documents = load_documents(source_directory, ignored_files)
    print(len(documents), " docs...")
    if not documents:
        print("No new documents to load.")
        return []

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    texts = text_splitter.split_documents(documents)
    print(f"Split into {len(texts)} chunks.")
    return texts


def does_vectorstore_exist(persist_directory: str) -> bool:
    """Checks if a vectorstore already exists in the specified directory."""
    index_path = os.path.join(persist_directory, 'index')
    if os.path.exists(index_path):
        required_files = ['chroma-collections.parquet', 'chroma-embeddings.parquet']
        if all(os.path.exists(os.path.join(persist_directory, f)) for f in required_files):
            return len(glob.glob(os.path.join(index_path, '*.bin'))) > 3
    return False


def ingest_files(source_directory, persist_directory):
    """Main function to ingest files into the vectorstore."""
    embeddings = HuggingFaceEmbeddings(model_name=embeddings_model_name)
    if does_vectorstore_exist(persist_directory):
        db = Chroma(persist_directory=persist_directory, embedding_function=embeddings, client_settings=CHROMA_SETTINGS)
        collection = db.get()
        texts = process_documents([metadata['source'] for metadata in collection['metadatas']],
                                  source_directory=source_directory)
        if texts:
            print("Creating embeddings and updating vectorstore...")
            db.add_documents(texts)
    else:
        print("Creating new vectorstore... "+persist_directory)
        texts = process_documents(source_directory=source_directory)
        if texts:
            while len(texts) > 5000:
                db = Chroma.from_documents(texts[:5001], embeddings, persist_directory=persist_directory)
                texts = texts[5000:]
                print(".")
            print("Creating embeddings...")
            db = Chroma.from_documents(texts, embeddings, persist_directory=persist_directory)

    if texts:
        db.persist()
        print("Ingestion complete!")
    else:
        print("No documents to ingest.")


def rebuild_shelf(shelf):
    src = os.path.join(get_root_dir(), shelf)
    db = get_db(shelf)
    shutil.rmtree(db)
    print("building db....")
    ingest_files(src, db)
    print("done")


if __name__ == '__main__':
    ingest_files("C:/Users/white/Documents/GitHub/chatJafu/exmples/demo",
                 "C:/Users/white/Documents/GitHub/chatJafu/exmples/demo/_db")