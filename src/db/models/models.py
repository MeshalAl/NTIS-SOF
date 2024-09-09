from db.database import engine
from db.models.bookmarks_model import BookmarkORM

BookmarkORM.metadata.create_all(bind=engine)
