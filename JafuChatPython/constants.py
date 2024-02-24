import os
from chromadb.config import Settings

# Define the folder for storing the database.
# If the environment variable 'PERSIST_DIRECTORY' is not set, default to 'db' folder.
PERSIST_DIRECTORY = os.environ.get('PERSIST_DIRECTORY', 'db')

# Define the Chroma settings using the 'Settings' class.
# Set the 'persist_directory' to the folder defined above and 'anonymized_telemetry' to False.
CHROMA_SETTINGS = Settings(
        persist_directory=PERSIST_DIRECTORY,
        anonymized_telemetry=False
)
