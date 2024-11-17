from app.database.repository.token import TokenRepository
from app.database.models.token_blocklist import TokenBlocklist
from typing import Dict, Any

class TokenUseCase:
    def __init__(self, token_repo: TokenRepository):
        self.token_repo = token_repo

    def create_token(self, data: Dict[str, Any]) -> bool:
        """Insert a new token record."""

        token_data = TokenBlocklist(**data)
        self.token_repo.create_token(token_data.to_json())

        return True
    
    def is_jti_blacklisted(self, jti: str):
        """Check if a token is blacklisted."""
        token = self.token_repo.find_token({"jti": jti})

        return True if token else False