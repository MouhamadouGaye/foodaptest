# app/schemas.py
from pydantic import BaseModel
from typing import Optional

class TokenData(BaseModel):
    user_id: Optional[str] = None  # user_id is optional in case it’s not present in the token payload
