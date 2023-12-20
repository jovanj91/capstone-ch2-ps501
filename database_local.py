import os
from sqlalchemy import create_engine, URL
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

db_host = "sql.freedb.tech"
db_user = "freedb_adminstuntingapp"
db_pass = "5qXJ%PzwqZrbyNT"
db_name = "freedb_stuntingapp"


url_object = URL.create(
    drivername="mysql+pymysql",
    host=db_host,
    username=db_user,
    password=db_pass,
    database=db_name,
)
engine = create_engine(url_object,)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    import models
    Base.metadata.create_all(bind=engine)