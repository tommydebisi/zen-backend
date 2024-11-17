from typing import Any, Dict, List, Optional, Union
from pymongo.database import Database as PyMongoDatabase
from pymongo.results import InsertOneResult, InsertManyResult, UpdateResult, DeleteResult
from pymongo.collection import Collection
from pymongo.cursor import Cursor
from bson import json_util
from app.utils.utils import serialize_document

class Database:
    def __init__(self, db: PyMongoDatabase):
        self.db: PyMongoDatabase = db

    def get_collection(self, collection: str) -> Collection:
        """Retrieve a collection from the database."""
        return self.db[collection]

    def get_all(self, collection: str) -> Cursor:
        """Retrieve all documents from a collection."""
        cursor = self.get_collection(collection).find()
        documents = list(cursor)
        return [serialize_document(doc) for doc in documents]


    def get_one(self, collection: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Retrieve a single document from a collection based on a query."""
        return self.get_collection(collection).find_one(query)

    def insert_one(self, collection: str, data: Dict[str, Any]) -> InsertOneResult:
        """Insert a single document into a collection."""
        return self.get_collection(collection).insert_one(data)

    def insert_many(self, collection: str, data: List[Dict[str, Any]]) -> InsertManyResult:
        """Insert multiple documents into a collection."""
        return self.get_collection(collection).insert_many(data)

    def update_one(self, collection: str, query: Dict[str, Any], data: Dict[str, Any]) -> UpdateResult:
        """Update a single document in a collection based on a query."""
        return self.get_collection(collection).update_one(query, {"$set": data})

    def update_many(self, collection: str, query: Dict[str, Any], data: Dict[str, Any]) -> UpdateResult:
        """Update multiple documents in a collection based on a query."""
        return self.get_collection(collection).update_many(query, {"$set": data})

    def delete_one(self, collection: str, query: Dict[str, Any]) -> DeleteResult:
        """Delete a single document from a collection based on a query."""
        return self.get_collection(collection).delete_one(query)

    def delete_many(self, collection: str, query: Dict[str, Any]) -> DeleteResult:
        """Delete multiple documents from a collection based on a query."""
        return self.get_collection(collection).delete_many(query)
