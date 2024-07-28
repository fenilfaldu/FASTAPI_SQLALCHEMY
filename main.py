from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field, Json
from sqlalchemy import create_engine, Column, String, JSON
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.dialects.postgresql import UUID
import uuid
import os, uvicorn

app = FastAPI()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@aviato-fastapi-database.cz26ie86qli4.us-east-1.rds.amazonaws.com/postgres")


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class DynamicData(Base):
    __tablename__ = "dynamic_data"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    data = Column(JSON, nullable=False)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class DynamicJSON(BaseModel):
    data: dict = Field(..., description="A dynamic JSON object")

@app.post("/add_users")
async def store_json(item: DynamicJSON, db: Session = Depends(get_db)):
    db_item = DynamicData(data=item.data)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return {"id": db_item.id, "data": db_item.data}

@app.get("/get_users")
async def get_users(db: Session = Depends(get_db)):
    users = db.query(DynamicData).all()
    return [{"id": user.id, "data": user.data} for user in users]

if __name__ == "__main__":
    config = uvicorn.Config(app=app, host="0.0.0.0", port=8080)
    server = uvicorn.Server(config)
    server.run()
