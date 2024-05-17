from typing import Optional

from sqlmodel import JSON, Field, SQLModel


class Aerich(SQLModel, table=True):
    __tablename__ = 'aerich'
    aerich_id: Optional[int] = Field(default=None, primary_key=True)
    version: str = Field(default=..., max_length=255)
    app: str = Field(default=..., max_length=100)
    content: dict = Field(default=..., sa_type=JSON)
