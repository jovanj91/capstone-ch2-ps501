import os
from sqlalchemy import create_engine, URL
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from google.cloud.sql.connector import Connector, IPTypes
db_host = os.environ[
    "INSTANCE_HOST"
]
db_user = os.environ.get('DB_USER')
db_pass = os.environ.get('DB_PASS')
db_name = os.environ.get('DB_NAME')
db_port = os.environ.get('DB_PORT')
unix_socket_path = os.environ[
    "INSTANCE_UNIX_SOCKET"
]

url_object = URL.create(
    drivername="mysql+pymysql",
    host=db_host,
    username=db_user,
    password=db_pass,
    database=db_name,
    port=db_port
    # query={"unix_socket": unix_socket_path}
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