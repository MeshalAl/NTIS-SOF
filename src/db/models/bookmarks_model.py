from db.models import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.sql import func

class BookmarkORM(Base):
    # find a way to make this auto generates from SOFUser model.
    __tablename__ = "bookmarks"
    
    user_id = Column(Integer, primary_key=True)
    account_id = Column(Integer)
    display_name = Column(String)
    user_age = Column(Integer, nullable=True)
    reputation = Column(Integer)
    location = Column(String, nullable=True)
    user_type = Column(String)
    last_access_date = Column(Integer, nullable=True)
    view_count = Column(Integer, nullable=True)
    question_count = Column(Integer, nullable=True)
    answer_count = Column(Integer, nullable=True)
    profile_image = Column(String, nullable=True)

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
