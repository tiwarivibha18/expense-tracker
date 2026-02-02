# Expense Tracker

## Tech Stack
- Backend: FastAPI, SQLite, SQLAlchemy
- Frontend: HTML + Vanilla JS

## Design Decisions
- Used SQLite for real persistence with minimal setup
- Used Numeric type for money correctness
- Added idempotency to handle retries and page refreshes

## Trade-offs
- Simple frontend (no framework)
- Basic error handling due to time constraint

## Not Implemented
- Authentication
- Pagination
- Styling framework

## Run Backend
uvicorn main:app --reload
