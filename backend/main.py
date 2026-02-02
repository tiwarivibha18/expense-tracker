from fastapi import FastAPI, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
import hashlib
from fastapi.responses import HTMLResponse
from sqlalchemy import func
import os

from . import models
from .database import SessionLocal, engine
from .schemas import ExpenseCreate, ExpenseOut

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Expense Tracker")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Idempotency key generator to handle retries
def generate_idempotency_key(expense: ExpenseCreate):
    raw = f"{expense.amount}{expense.category}{expense.description}{expense.date}"
    return hashlib.sha256(raw.encode()).hexdigest()

# POST /expenses - Create a new expense
@app.post("/expenses", response_model=ExpenseOut)
def create_expense(
    expense: ExpenseCreate,
    db: Session = Depends(get_db)
):
    key = generate_idempotency_key(expense)

    existing = db.query(Expense).filter(
        Expense.idempotency_key == key
    ).first()

    if existing:
        return existing

    db_expense = Expense(
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

# GET /expenses/summary - Total per category
@app.get("/expenses/summary")
def expense_summary(db: Session = Depends(get_db)):
    results = (
        db.query(
            Expense.category,
            func.sum(Expense.amount).label("total")
        )
        .group_by(Expense.category)
        .all()
    )

    return [
        {"category": r.category, "total": float(r.total)}
        for r in results
    ]

# GET /expenses - List expenses with optional filters
@app.get("/expenses", response_model=List[ExpenseOut])
def get_expenses(
    category: Optional[str] = None,
    sort: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Expense)

    if category:
        query = query.filter(Expense.category == category)

    if sort == "date_desc":
        query = query.order_by(Expense.date.desc())

    return query.all()

# GET / - Serve frontend HTML
@app.get("/", response_class=HTMLResponse)
def home():
    file_path = os.path.join(os.path.dirname(__file__), "index.html")
    with open(file_path, "r") as f:
        return f.read()
