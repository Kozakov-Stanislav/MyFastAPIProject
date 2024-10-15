from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    login = Column(String(length=50), index=True)  
    registration_date = Column(Date)

class Credit(Base):
    __tablename__ = "credits"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    issuance_date = Column(Date)
    return_date = Column(Date)
    actual_return_date = Column(Date)
    body = Column(Integer)
    percent = Column(Integer)

class Dictionary(Base):
    __tablename__ = "dictionary"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(length=100)) 

class Plan(Base):
    __tablename__ = "plans"
    id = Column(Integer, primary_key=True, index=True)
    period = Column(Integer)  
    sum = Column(Integer)
    category_id = Column(Integer, ForeignKey("dictionary.id"))

class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True, index=True)
    sum = Column(Integer)
    payment_date = Column(Date)
    credit_id = Column(Integer, ForeignKey("credits.id"))
    type_id = Column(Integer, ForeignKey("dictionary.id"))
