from pydantic import BaseModel, Field
from datetime import date

class ExpenseCreate(BaseModel):
    amount: float = Field(gt=0)
    category: str
    description: str
    date: date

class ExpenseOut(ExpenseCreate):
    id: int

    class Config:
        orm_mode = True
