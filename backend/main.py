from fastapi import FastAPI, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
import hashlib
from fastapi.responses import HTMLResponse
from database import SessionLocal, engine
import models, schemas
from sqlalchemy import func
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Expense Tracker")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def generate_idempotency_key(expense: schemas.ExpenseCreate):
    raw = f"{expense.amount}{expense.category}{expense.description}{expense.date}"
    return hashlib.sha256(raw.encode()).hexdigest()
    

@app.post("/expenses", response_model=schemas.ExpenseOut)
def create_expense(
    expense: schemas.ExpenseCreate,
    db: Session = Depends(get_db)
):
    key = generate_idempotency_key(expense)

    existing = db.query(models.Expense).filter(
        models.Expense.idempotency_key == key
    ).first()

    if existing:
        return existing

    db_expense = models.Expense(
        amount=expense.amount,
        category=expense.category,
        description=expense.description,
        date=expense.date,
        idempotency_key=key
    )

    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense

@app.get("/expenses/summary")
def expense_summary(db: Session = Depends(get_db)):
    results = (
        db.query(
            models.Expense.category,
            func.sum(models.Expense.amount).label("total")
        )
        .group_by(models.Expense.category)
        .all()
    )

    return [
        {"category": r.category, "total": float(r.total)}
        for r in results
    ]

@app.get("/expenses", response_model=List[schemas.ExpenseOut])
def get_expenses(
    category: Optional[str] = None,
    sort: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Expense)

    if category:
        query = query.filter(models.Expense.category == category)

    if sort == "date_desc":
        query = query.order_by(models.Expense.date.desc())

    return query.all()


@app.get("/", response_class=HTMLResponse)
def home():
    with open("index.html") as f:
        return f.read()