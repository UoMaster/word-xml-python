from pydantic import BaseModel, Field
from datetime import datetime


class WeigetRecord(BaseModel):
    label_key: str
    type: str
    options: list[str]
    hit_count: int
    consistency_count: int
    un_consistency_count: int
    confidence: float
    create_time: datetime = Field(default_factory=datetime.now)
    update_time: datetime = Field(default_factory=datetime.now)
