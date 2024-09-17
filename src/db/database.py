import os
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm.session import Session
from contextlib import contextmanager
from typing import Any
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
import click


class DatabaseManager:

    def __init__(self, database_url: str | None = None) -> None:

        self.load_env()
        database_url = database_url or os.environ.get("DATABASE_URL")
        if not database_url:
            raise ValueError(
                "DATABASE_URL, either provided as an argument or in the .env file, is required"
            )

        self.engine = create_engine(database_url)

    @contextmanager
    def get_session(self) -> Generator[Session, Any, None]:
        session = Session(self.engine)
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def check_connection(self) -> bool | SQLAlchemyError:
        try:
            with self.engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            return True
        except SQLAlchemyError as e:
            raise click.ClickException(f"Database connection failed: {e}")

    @staticmethod
    def load_env():
        from pathlib import Path
        from dotenv import load_dotenv

        env_path = Path(__file__).parent.parent.parent / ".env"
        is_loaded = load_dotenv(dotenv_path=env_path)
        if not is_loaded:
            raise FileNotFoundError(f"No .env file found, target: {env_path}")
