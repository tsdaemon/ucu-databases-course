import os

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

Base = declarative_base()

# TODO: Define your data classes here

# TODO: Set credentials for your user defined in db.sql
user = ''
password = ''
database = 'university'
host = os.environ.get('DB_HOST', 'localhost')
connection_string = 'mysql://{user}:{password}@{host}/{database}'.format(
    user=user, password=password, database=database, host=host
)

engine = create_engine()
Base.metadata.create_all(engine)