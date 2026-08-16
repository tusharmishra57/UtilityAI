import os
import sys
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models, auth, ai_service
from datetime import date

def seed_db():
    db = SessionLocal()
    try:
        # Seed Documents
        print("Seeding Documents...")
        docs_dir = os.path.join(os.path.dirname(__file__), "..")
        doc_files = ["billing_guide.txt", "energy_saving.txt", "payment_policy.txt"]
        
        for file_name in doc_files:
            file_path = os.path.join(docs_dir, file_name)
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Check if exists
                existing = db.query(models.Document).filter(models.Document.title == file_name).first()
                if not existing:
                    print(f"Adding {file_name}...")
                    # Generate embedding
                    embedding = ai_service.get_embedding(content)
                    doc = models.Document(title=file_name, content=content, embedding=embedding)
                    db.add(doc)
            else:
                print(f"Warning: {file_name} not found in {docs_dir}")

        # Seed Dummy Customer
        existing_user = db.query(models.Customer).filter(models.Customer.email == "test@example.com").first()
        if not existing_user:
            print("Creating test customer...")
            hashed_pw = auth.get_password_hash("password123")
            user = models.Customer(name="Test User", email="test@example.com", password_hash=hashed_pw)
            db.add(user)
            db.commit()
            db.refresh(user)
            
            # Add consumption
            print("Adding consumption data...")
            c1 = models.Consumption(customer_id=user.id, month="2023-06", consumption_kwh=210)
            c2 = models.Consumption(customer_id=user.id, month="2023-07", consumption_kwh=245)
            c3 = models.Consumption(customer_id=user.id, month="2023-08", consumption_kwh=270)
            db.add_all([c1, c2, c3])
            
            # Add bills
            print("Adding bills...")
            b1 = models.Bill(customer_id=user.id, billing_month="2023-07", consumption_kwh=245, amount=1820, status="PAID", due_date=date(2023, 8, 20))
            b2 = models.Bill(customer_id=user.id, billing_month="2023-08", consumption_kwh=270, amount=2050, status="UNPAID", due_date=date(2023, 9, 20))
            db.add_all([b1, b2])
            
            db.commit()
        
        print("Database seeding completed.")
    except Exception as e:
        print(f"Error during seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_db()
