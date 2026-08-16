from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date, datetime

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class ConsumptionResponse(BaseModel):
    id: int
    month: str
    consumption_kwh: float

    class Config:
        from_attributes = True

class BillResponse(BaseModel):
    id: int
    billing_month: str
    consumption_kwh: float
    amount: float
    status: str
    due_date: date

    class Config:
        from_attributes = True

class PaymentRequest(BaseModel):
    bill_id: int

class PaymentResponse(BaseModel):
    id: int
    bill_id: int
    amount: float
    transaction_id: str
    status: str
    payment_date: datetime

    class Config:
        from_attributes = True

class AIQuery(BaseModel):
    question: str

class AIResponse(BaseModel):
    answer: str
