from sqlalchemy import create_engine, Column, Integer, String, BigInteger, Boolean, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String(100))
    first_name = Column(String(100))
    last_name = Column(String(100))
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)

class Payment(Base):
    __tablename__ = 'payments'
    
    id = Column(Integer, primary_key=True)
    payment_id = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(BigInteger, nullable=False)
    amount = Column(Integer, nullable=False)
    currency = Column(String(10), nullable=False)
    product = Column(String(50), nullable=False)
    status = Column(String(20), default='pending')
    payment_method = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    price_stars = Column(Integer, default=0)
    price_rub = Column(Integer, default=0)
    price_usd = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

def init_db():
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)

SessionLocal = init_db()
