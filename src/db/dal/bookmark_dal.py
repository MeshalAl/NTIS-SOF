from db.models.models import BookmarkORM
from db.database import engine
from models.bookmark_model import Bookmark as BookmarkModel
from sqlalchemy.orm import Session

def create_bookmark(bookmark: BookmarkModel, session: Session):
    db_bookmark = BookmarkORM(**bookmark.model_dump())
    session.add(db_bookmark)
    return db_bookmark

def get_bookmark_by_id(user_id: int, session: Session):
    return session.query(BookmarkORM).filter(BookmarkORM.user_id == user_id).first()

def get_bookmarks(page_size: int, page: int, session: Session):
    # page of 1 means no offset, 1-1 = 0, 0 * page_size = 0 so no offset
    return session.query(BookmarkORM).limit(page_size).offset((page - 1) * page_size).all()

def delete_bookmark(user_id: int, session: Session):
    bookmark = get_bookmark_by_id(user_id, session)
    if bookmark:
        session.delete(bookmark)
        session.commit()
        return True
    return False
