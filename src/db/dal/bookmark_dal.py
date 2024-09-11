from db.models.models import BookmarkORM
from db.database import engine
from models.bookmark_model import Bookmark, BookmarkDB
from sqlalchemy.orm import Session
from sqlalchemy import select, delete, update, insert
from typing import List, Tuple
from click import secho, confirm


def create_bookmarks(session: Session, bookmark: List[Bookmark]):

    if not bookmark:
        raise ValueError("No bookmark data provided")

    user_ids = [user.user_id for user in bookmark]
    query = select(BookmarkORM).filter(BookmarkORM.user_id.in_(user_ids))
    existing_bookmarks = session.scalars(query).all()
    existing_user_ids = [bookmark.user_id for bookmark in existing_bookmarks]
    new_bookmarks = [user for user in bookmark if user.user_id not in existing_user_ids]

    if new_bookmarks:
        session.bulk_save_objects(
            [BookmarkORM(**user.model_dump()) for user in new_bookmarks]
        )
        secho(f"{len(new_bookmarks)}/{len(bookmark)} bookmarks added", fg="green")
    else:
        raise ValueError("All bookmarks already exists")


def get_bookmarks(
    session: Session, page_size: int, page: int, user_ids: List[int] | None = None
) -> list[BookmarkDB] | None:
    # page of 1 means no offset, 1-1 = 0, 0 * page_size = 0 so no offset
    if page <= 0 or page_size <= 0:
        raise ValueError("Page number or page size cannot be less than 1")
    if user_ids:
        query = (
            select(BookmarkORM)
            .filter(BookmarkORM.user_id.in_(user_ids))
            .limit(page_size)
            .offset((page - 1) * page_size)
        )
    else:
        query = select(BookmarkORM).limit(page_size).offset((page - 1) * page_size)
    results = session.scalars(query).all()
    if results:
        return [BookmarkDB.model_validate(result) for result in results]
    return None


def delete_bookmarks(
    session: Session,
    user_ids: Tuple[int] | None = None,
    bookmarks: List[Bookmark] | None = None,
):
    if not (bookmarks or bool(user_ids)):
        raise ValueError("No bookmark data provided")

    if bookmarks:
        ids_to_delete = [bookmark.user_id for bookmark in bookmarks]
    else:
        ids_to_delete = user_ids

    if isinstance(ids_to_delete, tuple):
        query = select(BookmarkORM).filter(BookmarkORM.user_id.in_(ids_to_delete))
        existing_bookmarks = session.scalars(query).all()
        existing_user_ids = [bookmark.user_id for bookmark in existing_bookmarks]

        bookmarks_to_delete = [
            user_id for user_id in ids_to_delete if user_id in existing_user_ids
        ]

        if bookmarks_to_delete:
            delete_query = delete(BookmarkORM).where(
                BookmarkORM.user_id.in_(bookmarks_to_delete)
            )
            result = session.execute(delete_query)

            secho(
                f"{result.rowcount}/{len(ids_to_delete)} bookmarks deleted", fg="green"
            )
        else:
            raise ValueError("No bookmarks found to delete")

    else:
        raise ValueError("internal delete error")


def delete_all_bookmarks(session: Session):

    delete_query = delete(BookmarkORM)
    result = session.execute(delete_query)
    secho(f"All bookmarks deleted. {result.rowcount} rows removed.", fg="green")


def update_bookmarks(bookmarks: List[Bookmark], session: Session) -> int:
    if not bookmarks:
        raise ValueError("No bookmark data provided")
    affected_rows = session.execute(
        update(BookmarkORM), [bookmark.model_dump() for bookmark in bookmarks]
    )

    return affected_rows.rowcount
