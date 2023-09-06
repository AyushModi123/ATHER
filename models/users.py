from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

Base = declarative_base()

class UsersModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(500), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    verify_status = Column(Boolean, default=False)

    