from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from typing import List

import models, schemas, database, auth, ai_service

app = FastAPI(title="UtilityAI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to UtilityAI API"}

# --- AUTH ---
@app.post("/auth/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = db.query(models.Customer).filter(models.Customer.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = auth.get_password_hash(user.password)
    new_user = models.Customer(name=user.name, email=user.email, password_hash=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/auth/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.Customer).filter(models.Customer.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/auth/me", response_model=schemas.UserResponse)
def read_users_me(current_user: models.Customer = Depends(auth.get_current_user)):
    return current_user

# --- DATA ---
@app.get("/consumption", response_model=List[schemas.ConsumptionResponse])
def get_consumption(db: Session = Depends(database.get_db), current_user: models.Customer = Depends(auth.get_current_user)):
    return db.query(models.Consumption).filter(models.Consumption.customer_id == current_user.id).order_by(models.Consumption.month).all()

@app.get("/bills", response_model=List[schemas.BillResponse])
def get_bills(db: Session = Depends(database.get_db), current_user: models.Customer = Depends(auth.get_current_user)):
    return db.query(models.Bill).filter(models.Bill.customer_id == current_user.id).order_by(models.Bill.due_date.desc()).all()

@app.post("/payments", response_model=schemas.PaymentResponse)
def make_payment(payment: schemas.PaymentRequest, db: Session = Depends(database.get_db), current_user: models.Customer = Depends(auth.get_current_user)):
    # Simple transaction
    bill = db.query(models.Bill).filter(models.Bill.id == payment.bill_id, models.Bill.customer_id == current_user.id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    if bill.status == "PAID":
        raise HTTPException(status_code=400, detail="Bill is already paid")
    
    try:
        # Create payment record
        import uuid
        new_payment = models.Payment(
            bill_id=bill.id,
            amount=bill.amount,
            transaction_id=str(uuid.uuid4()),
            status="SUCCESS"
        )
        db.add(new_payment)
        
        # Update bill
        bill.status = "PAID"
        
        db.commit()
        db.refresh(new_payment)
        return new_payment
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Payment transaction failed")

# --- AI ---
@app.post("/ai/ask", response_model=schemas.AIResponse)
def ask_ai(query: schemas.AIQuery, db: Session = Depends(database.get_db), current_user: models.Customer = Depends(auth.get_current_user)):
    question = query.question
    
    # 1. Get structured data context
    recent_consumptions = db.query(models.Consumption).filter(models.Consumption.customer_id == current_user.id).order_by(models.Consumption.month.desc()).limit(3).all()
    recent_bills = db.query(models.Bill).filter(models.Bill.customer_id == current_user.id).order_by(models.Bill.due_date.desc()).limit(2).all()
    
    structured_context = f"Customer Name: {current_user.name}\n"
    structured_context += "Recent Consumption (last 3 months):\n"
    for c in reversed(recent_consumptions):
        structured_context += f"- {c.month}: {c.consumption_kwh} kWh\n"
    
    if len(recent_consumptions) >= 2:
        prev = recent_consumptions[1].consumption_kwh
        curr = recent_consumptions[0].consumption_kwh
        if prev > 0:
            change = ((curr - prev) / prev) * 100
            structured_context += f"Calculated change from previous month: {change:.2f}%\n"

    structured_context += "\nRecent Bills:\n"
    for b in recent_bills:
        structured_context += f"- {b.billing_month}: Rs {b.amount} (Status: {b.status})\n"
        
    # 2. Get document context via RAG
    doc_context = ""
    try:
        q_emb = ai_service.get_embedding(question)
        if q_emb:
            from pgvector.sqlalchemy import Vector
            # Perform similarity search
            docs = db.query(models.Document).order_by(models.Document.embedding.cosine_distance(q_emb)).limit(2).all()
            if docs:
                doc_context = "\nRelevant Utility Documents:\n"
                for d in docs:
                    doc_context += f"{d.content}\n"
    except Exception as e:
        print(f"RAG search error: {e}")
        
    full_context = structured_context + "\n" + doc_context
    
    # 3. Ask Gemini
    answer = ai_service.generate_answer(full_context, question)
    return {"answer": answer}
