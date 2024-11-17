from app.database.base import Database
from app.database.models.token_blocklist import TokenBlocklist
from typing import Dict, Any

class TokenRepository:
    def __init__(self, db: Database):
        self.db = db

    def create_token(self, data: Dict[str, Any]):
        """Insert a new token record."""
        return self.db.insert_one(TokenBlocklist.__name__, data)
    
    def find_and_delete_token(self, query: Dict[str, Any]):
        """Find a token by query and delete the record."""
        return self.db.delete_one(TokenBlocklist.__name__, query)
    
    def find_token(self, query: Dict[str, Any]):
        """Find a token by query."""
        return self.db.get_one(TokenBlocklist.__name__, query)
    
    def find_all_tokens(self):
        """Fetch all tokens."""
        return self.db.get_all(TokenBlocklist.__name__)