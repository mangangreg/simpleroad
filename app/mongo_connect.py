import os
from pathlib import Path

from pymongo import MongoClient
from dotenv import load_dotenv

HERE = Path(__file__).parent

class MongoConnect:
    def __init__(self, user=None, password=None, host=None, port=None, database=None, env_file=HERE/'.mongo.env'):

        # Load the env file
        load_dotenv(env_file)

        self.user = user or os.getenv('MONGO_USER')
        self.password = password or os.getenv('MONGO_PASSWORD')
        self.host = host or os.getenv('MONGO_HOST') or 'localhost'
        self.port = port or os.getenv('MONGO_PORT') or 27017
        self.database = database or os.getenv('MONGO_DATABASE')

        # Build the URI
        self.URI = self._constructURI()

        # Initialise connection and db
        self.connection = None
        self.db = None

    def _constructURI(self):
        return f"mongodb://{self.user}:{self.password}@{self.host}:{self.port}"

    def connect(self):
        self.connection = MongoClient(self.URI)
        self.db = self.connection[self.database]
