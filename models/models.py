from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

Base = declarative_base()

class UsersModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(500), unique=True, nullable=False)
    password = Column(String(500), nullable=False)
    verify_status = Column(Boolean, default=False)
    # education = relationship('education', backref='users')
    # experience = relationship('experience', backref='users')
    # skills = relationship('skills', backref='users')

class UserDetailsModel(Base):
    __tablename__ = 'user_details'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String(255))
    email = Column(String(255))
    contact = Column(String(255))
    location = Column(String(255))
    linkedin_link = Column(String(255))
    github_link = Column(String(255))
    leetcode_link = Column(String(255))
    codechef_link = Column(String(255))
    codeforces_link = Column(String(255))

class EducationModel(Base):
    __tablename__ = 'education'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String(255))
    stream = Column(String(255))
    score = Column(String(255))
    location = Column(String(255))
    graduation_year = Column(String(255))

class ExperienceModel(Base):
    __tablename__ = 'experience'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    company_name = Column(String(255))
    role = Column(String(255))
    role_desc = Column(String(2048))
    start_date = Column(String(255))
    end_date = Column(String(255))

class SkillsModel(Base):
    __tablename__ = 'skills'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    skills = Column(String(1024))
