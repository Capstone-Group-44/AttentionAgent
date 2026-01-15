from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    uid: str
    username: str
    email: str
    display_name: Optional[str] = None
    created_at: Optional[str] = None
