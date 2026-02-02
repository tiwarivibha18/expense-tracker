from sqlalchemy import Column, Integer, String, Date, DateTime, Numeric, UniqueConstraint
from datetime import datetime
from .database import Base

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Numeric(10, 2), nullable=False)
    category = Column(String, index=True)
    description = Column(String)
    date = Column(Date, nullable=False)
    idempotency_key = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("idempotency_key", name="uq_idempotency_key"),
    )
