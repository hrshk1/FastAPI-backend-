# A session is an object that lets your application talk to the database, keeps track of changes, and saves or discards them when you're done.


#sessionmaker is a class helps to make sessions 
from sqlalchemy.orm import sessionmaker
#engine tells which database, which user, and which password to use to connect to the database. It also tells which database driver to use.
from sqlalchemy import create_engine
import os

#db_url structure is as follows: "database_type://username:password@host:port/database_name"
#make sure you have created a database named fastapi in your postgresql server before running the code below. You can create a database using pgAdmin or psql command line tool.
db_url = os.getenv("DATABASE_URL", "postgresql://postgres:hrshk1@localhost:5432/fastapi")
engine = create_engine(db_url)

#always make autocommit and autoflush to false, because we want to control when the changes are committed to the database and when the session is flushed. This gives us more control over the transaction and allows us to handle errors more gracefully.
session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
