from app.database import RecordRepository
from app.database.models.record import Record
from werkzeug.datastructures import MultiDict
from pymongo.errors import PyMongoError
from bson import ObjectId
from typing import Dict, Any, Tuple
from datetime import datetime

class RecordUseCase:
    def __init__(self, record_repo: RecordRepository):
        self.record_repo = record_repo

    def create_record(self, data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Create a new record."""
        record_data = Record(**data)
        bson_data = record_data.to_bson()

        # Insert into database
        result_data = self.record_repo.create_record(bson_data)
        if not result_data:
            return False, {
                "message": "Record creation failed."
            }
        
        # stringify the ObjectId
        result_data['_id'] = str(result_data['_id'])
    
        return True, {
            "message": "Record created successfully.",
            "data": result_data
        }

    def get_all_records(self) -> Tuple[bool, Dict[str, Any]]:
        """Fetch all records."""
        records =  self.record_repo.find_and_sort_by("start_date", -1)

        return True, {
            "message": "Records found.",
            "data": records
        }
        

    def get_record_by_id(self, record_id: str) -> Tuple[bool, Dict[str, Any]]:
        """Fetch a record by ID."""
        record =  self.record_repo.get_by_id(record_id)
        if not record:
            return False, {
                "message": "Record not found."
            }
        
        # stringify the ObjectId
        record['_id'] = str(record['_id'])
        
        return True, {
            "message": "Record found.",
            "data": record
        }

    def update_record(self, record_id: str, data: MultiDict) -> Tuple[bool, Dict[str, Any]]:
        """
        Update a record by its ID.
        If no record matches the ID or no changes were made, return an appropriate message.
        """
        try:
            # Add or update the `updated_at` field
            data['updated_at'] = datetime.now()
            
            result_data = self.record_repo.find_and_update_record({"_id": ObjectId(record_id)}, data)
            if result_data.matched_count == 0:
                return False, {
                    "message": "Record not found.",
                }
            
            # check if any changes were made
            if result_data.modified_count == 0:
                return False, {
                    "message": "No changes were made.",
                }
            
            return True, {
                "message": "Record updated successfully.",
            }
        except PyMongoError as e:
            raise RuntimeError("An error occurred while updating the record: {str(e)}")
        
    def delete_record(self, record_id: str) -> Tuple[bool, Dict[str, Any]]:
        """Delete a record by its ID."""
        try:
            result_data = self.record_repo.find_and_delete_record({"_id": ObjectId(record_id)})
            if result_data.deleted_count == 0:
                return False, {
                    "message": "Record not found."
                }
            
            return True, {
                "message": "Record deleted successfully."
            }
        except PyMongoError as e:
            raise RuntimeError(f"An error occurred while deleting the record: {str(e)}")