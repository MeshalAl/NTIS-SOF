import os
from sqlalchemy import create_engine
from sqlalchemy.orm.session import Session 
from db.utility import load_dotenv


load_dotenv()

database_url = os.environ.get('DATABASE_URL')

engine = create_engine(database_url)

def get_session():

    with Session(engine) as session:
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
