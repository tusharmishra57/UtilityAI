from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Date, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from database import Base

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    consumptions = relationship("Consumption", back_populates="customer")
    bills = relationship("Bill", back_populates="customer")

class Consumption(Base):
    __tablename__ = "consumption"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    month = Column(String, nullable=False, index=True) # e.g., '2023-07'
    consumption_kwh = Column(Float, nullable=False)

    customer = relationship("Customer", back_populates="consumptions")

class Bill(Base):
    __tablename__ = "bills"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    billing_month = Column(String, nullable=False)
    consumption_kwh = Column(Float, nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String, default="UNPAID") # UNPAID, PAID
    due_date = Column(Date, nullable=False)

    customer = relationship("Customer", back_populates="bills")
    payments = relationship("Payment", back_populates="bill")

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    bill_id = Column(Integer, ForeignKey("bills.id"), nullable=False)
    amount = Column(Float, nullable=False)
    transaction_id = Column(String, unique=True, index=True)
    status = Column(String, default="SUCCESS")
    payment_date = Column(DateTime(timezone=True), server_default=func.now())

    bill = relationship("Bill", back_populates="payments")

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(384)) # 384 for all-MiniLM-L6-v2
