from pydantic import BaseModel, Field
from models.sof_models import SOFUser
from datetime import datetime

class Bookmark(SOFUser):
    created_at: datetime | None = Field(default_factory=datetime.now)
    updated_at: datetime | None = Field(default_factory=datetime.now)

class BookmarkDB(Bookmark):
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attribute = True

