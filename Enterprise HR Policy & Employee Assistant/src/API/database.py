from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.engine import URL


db_url = URL.create(
    drivername="postgresql+psycopg",
    username="postgres",
    password="root@123",
    host="localhost",
    port=5432,
    database="employee_details",
)


engine = create_engine(db_url)


session = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


Base = declarative_base()


def get_db():
    db = session()

    try:
        yield db
    finally:
        db.close()