from db.database import DatabaseManager
from db.models.bookmarks_model import BookmarkORM

engine = DatabaseManager().engine

BookmarkORM.metadata.create_all(bind=engine)
