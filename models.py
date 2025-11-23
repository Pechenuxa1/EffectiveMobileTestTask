import enum

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()


class RoleType(enum.Enum):
    USER = "User"
    SUPERUSER = "Superuser"
    ADMIN = "Admin"


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    firstname = Column(String(50), nullable=False)
    surname = Column(String(50), nullable=False)
    middle_name = Column(String(50), nullable=True)
    email = Column(String(50), unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'))

    role = relationship('Role', back_populates='users', lazy='selectin')


class Role(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True)
    name = Column(Enum(RoleType), unique=True, nullable=False)

    users = relationship("User", back_populates="role", uselist=True, lazy='selectin')


class BusinessObject(Base):
    __tablename__ = 'business_objects'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))


class AccessRule(Base):
    __tablename__ = 'access_rules'

    id = Column(Integer, primary_key=True)
    create_permission = Column(Boolean, nullable=False, default=True)
    read_permission = Column(Boolean, nullable=False, default=True)
    read_all_permission = Column(Boolean, nullable=False, default=False)
    update_permission = Column(Boolean, nullable=False, default=True)
    update_all_permission = Column(Boolean, nullable=False, default=False)
    delete_permission = Column(Boolean, nullable=False, default=True)
    delete_all_permission = Column(Boolean, nullable=False, default=False)
    role_id = Column(Integer, ForeignKey('roles.id'))
    business_object_id = Column(Integer, ForeignKey('business_objects.id'))

    role = relationship("Role", backref="access_rules", lazy='selectin')
    business_object = relationship("BusinessObject", backref="access_rules", lazy='selectin')

    __table_args__ = (
        UniqueConstraint('role_id', 'business_object_id'),
    )
