from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Job(Base):
    job_id = Column(Integer, primary_key=True)


class Employer(Base):
    employer_id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)

class Major(Base):
    major_id = Column(Integer, primary_key=True)
    name = Column(Integer, primary_key=True)