from sqlalchemy import Column, Integer, String, Boolean, Table, ForeignKey
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql import func
from sqlalchemy.orm import sessionmaker, relationship
from flask_security import UserMixin, RoleMixin
from flask_security.models import fsqla_v3 as fsqla
import bcrypt




engine = create_engine("mysql+pymysql://root:root@localhost/db_cekjantung")

Base = declarative_base()
metadata = MetaData()
metadata.bind = engine

# roles_users = Table('roles_users', metadata,
#         Column('user_id', Integer(), ForeignKey('tb_users.user_id')),
#         Column('role_id', Integer(), ForeignKey('tb_roles.role_id')))

class Users(Base):
    __tablename__ = "tb_users"
    user_id = Column(Integer, primary_key = True, autoincrement=True)
    user_name = Column(String(255), unique=True)
    user_email = Column(String(255))
    user_password = Column(String(255)) #hashed
    active = Column(Boolean)
    role_id = Column(Integer,ForeignKey('tb_roles.role_id'))
    # user_roles = relationship('Roles', secondary=roles_users, backref='roled')
    user_roles = relationship('Roles', backref='roled')
    def __init__(self, username, email, active):
        self.user_name = username
        self.user_email = email
        self.active = active

    def set_password(self, password):
        hashedpassword = bcrypt.hashpw(password, bcrypt.gensalt())
        self.user_password = hashedpassword.decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password, self.user_password.encode('utf-8'))

    def __repr__(self):
        return f"<User(id={self.user_id}, username='{self.user_name}', email='{self.user_email}')>"

class Roles(Base):
    __tablename__ = 'tb_roles'
    role_id = Column(Integer(), primary_key=True)
    role_name = Column(String(80), unique=True)


def create_tables():
   metadata.create_all

Session = sessionmaker(bind=engine)