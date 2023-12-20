from database_local import Base
from flask_security import UserMixin, RoleMixin, AsaList
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy import Boolean, DateTime, Column, Integer, \
                    String, ForeignKey, Double, Date, func

class RolesUsers(Base):
    __tablename__ = 'roles_users'
    id = Column(Integer(), primary_key=True)
    user_id = Column('user_id', Integer(), ForeignKey('user.id'))
    role_id = Column('role_id', Integer(), ForeignKey('role.id'))

class Role(Base, RoleMixin):
    __tablename__ = 'role'
    id = Column(Integer(), primary_key=True)
    name = Column(String(80), unique=True)
    description = Column(String(255))
    permissions = Column(MutableList.as_mutable(AsaList()), nullable=True)

class User(Base, UserMixin):
    __tablename__ = 'user'
    id = Column(Integer(), primary_key=True)
    email = Column(String(255), unique=True)
    username = Column(String(255), unique=True, nullable=True)
    password = Column(String(255), nullable=False)
    last_login_at = Column(DateTime())
    current_login_at = Column(DateTime())
    last_login_ip = Column(String(100))
    current_login_ip = Column(String(100))
    login_count = Column(Integer)
    active = Column(Boolean())
    fs_uniquifier = Column(String(64), unique=True, nullable=False)
    confirmed_at = Column(DateTime())
    roles = relationship('Role', secondary='roles_users', backref=backref('users', lazy='dynamic'))
    child_data = relationship('ChildrenData', backref='user', lazy='dynamic')
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"

class ChildrenData(Base):
    __tablename__ = 'childrenData'
    id = Column(Integer(), primary_key=True)
    user_id = Column('user_id', Integer(), ForeignKey('user.id'))
    first_name = Column(String(24))
    last_name = Column(String(24))
    child_dob = Column(Date())
    gender = Column(Integer())
    stunt_check = relationship('StuntCheck', backref='child', lazy='dynamic')

class StuntCheck(Base):
    __tablename__ = 'stuntCheck'
    id = Column(Integer(), primary_key=True)
    child_id = Column('child_id', Integer(), ForeignKey('childrenData.id'))
    age = Column(Integer())
    weight = Column(Double())
    height = Column(Double())
    bodyMassIndex = Column(Double())
    checkResult = Column(String(24))
    checked_at = Column(DateTime())
