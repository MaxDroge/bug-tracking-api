from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import declarative_base, sessionmaker

# -----------------------------
# DATABASE SETUP
# -----------------------------

DATABASE_URL = "sqlite:///./bugs.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # needed for SQLite with FastAPI
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


# -----------------------------
# DATABASE MODEL
# -----------------------------

class Bug(Base):
    __tablename__ = "bugs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String, default="open")
    priority = Column(String, default="medium")


# Create the table if it does not already exist
Base.metadata.create_all(bind=engine)


# -----------------------------
# Pydantic SCHEMAS
# -----------------------------

class BugCreate(BaseModel):
    title: str
    description: str
    priority: Optional[str] = "medium"


class BugUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None


class BugResponse(BaseModel):
    id: int
    title: str
    description: str
    status: str
    priority: str

    class Config:
        from_attributes = True


# -----------------------------
# FASTAPI APP
# -----------------------------

app = FastAPI(title="Bug Tracking API")


# -----------------------------
# ROUTES
# -----------------------------

@app.get("/")
def home():
    return {"message": "Bug Tracking API is running"}


@app.post("/bugs", response_model=BugResponse)
def create_bug(bug: BugCreate):
    db = SessionLocal()

    valid_priorities = ["low", "medium", "high"]
    if bug.priority not in valid_priorities:
        db.close()
        raise HTTPException(status_code=400, detail="Priority must be low, medium, or high")

    new_bug = Bug(
        title=bug.title,
        description=bug.description,
        priority=bug.priority
    )

    db.add(new_bug)
    db.commit()
    db.refresh(new_bug)
    db.close()

    return new_bug


@app.get("/bugs", response_model=List[BugResponse])
def get_bugs():
    db = SessionLocal()
    bugs = db.query(Bug).all()
    db.close()
    return bugs


@app.get("/bugs/{bug_id}", response_model=BugResponse)
def get_bug(bug_id: int):
    db = SessionLocal()
    bug = db.query(Bug).filter(Bug.id == bug_id).first()
    db.close()

    if not bug:
        raise HTTPException(status_code=404, detail="Bug not found")

    return bug


@app.put("/bugs/{bug_id}", response_model=BugResponse)
def update_bug(bug_id: int, updated_bug: BugUpdate):
    db = SessionLocal()
    bug = db.query(Bug).filter(Bug.id == bug_id).first()

    if not bug:
        db.close()
        raise HTTPException(status_code=404, detail="Bug not found")

    valid_statuses = ["open", "in-progress", "closed"]
    valid_priorities = ["low", "medium", "high"]

    if updated_bug.status is not None:
        if updated_bug.status not in valid_statuses:
            db.close()
            raise HTTPException(status_code=400, detail="Status must be open, in-progress, or closed")
        bug.status = updated_bug.status

    if updated_bug.priority is not None:
        if updated_bug.priority not in valid_priorities:
            db.close()
            raise HTTPException(status_code=400, detail="Priority must be low, medium, or high")
        bug.priority = updated_bug.priority

    if updated_bug.title is not None:
        bug.title = updated_bug.title

    if updated_bug.description is not None:
        bug.description = updated_bug.description

    db.commit()
    db.refresh(bug)
    db.close()

    return bug


@app.delete("/bugs/{bug_id}")
def delete_bug(bug_id: int):
    db = SessionLocal()
    bug = db.query(Bug).filter(Bug.id == bug_id).first()

    if not bug:
        db.close()
        raise HTTPException(status_code=404, detail="Bug not found")

    db.delete(bug)
    db.commit()
    db.close()

    return {"message": f"Bug {bug_id} deleted successfully"}