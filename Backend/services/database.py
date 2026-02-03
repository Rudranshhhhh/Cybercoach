from pymongo import MongoClient
from pymongo.server_api import ServerApi
from config import Config


class Database:
    """MongoDB database connection singleton."""
    
    def __init__(self):
        """Initialize the database connection."""
        self.client = None
        self.db = None
        self._connect()
    
    def _connect(self):
        """Establish database connection."""
        if not Config.MONGO_URI:
            print("WARNING: MONGO_URI not set in environment")
            return
        
        try:
            print(f"Connecting to MongoDB...")
            # Create client with Server API version 1 for Atlas compatibility
            self.client = MongoClient(
                Config.MONGO_URI,
                server_api=ServerApi('1'),
                serverSelectionTimeoutMS=10000,
                connectTimeoutMS=10000
            )
            
            # Ping to confirm connection
            self.client.admin.command('ping')
            print("MongoDB connected successfully!")
            
            # Get the cybercoach database
            self.db = self.client.cybercoach
            
        except Exception as e:
            print(f"MongoDB connection error: {type(e).__name__}: {e}")
            self.client = None
            self.db = None
    
    def is_connected(self) -> bool:
        """Check if database is connected."""
        return self.db is not None
    
    def get_collection(self, name: str):
        """Get a collection by name."""
        if self.db is None:
            return None
        return self.db[name]


# Singleton instance
database = Database()
