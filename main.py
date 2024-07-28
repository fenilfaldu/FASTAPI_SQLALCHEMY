from fastapi import FastAPI,BackgroundTasks, HTTPException, Depends
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import BaseModel,EmailStr, Field, Json
from sqlalchemy import create_engine, Column, String, JSON
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.dialects.postgresql import UUID
import uuid
from typing import List, Optional
import os, uvicorn

app = FastAPI()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@aviato-fastapi-database.cz26ie86qli4.us-east-1.rds.amazonaws.com/postgres")

conf = ConnectionConfig(
    MAIL_USERNAME="fenilfaldu143@gmail.com",
    MAIL_PASSWORD="add_password_here", #removed the password as this is going to be pushed to github
    MAIL_FROM="fenilfaldu143@gmail.com",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True
)

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

class EmailSchema(BaseModel):
    email: List[EmailStr]


class DynamicJSON(BaseModel):
    data: dict = Field(..., description="A dynamic JSON object")

class UpdateDynamicJSON(BaseModel):
    id: uuid.UUID
    data: Optional[dict] = Field(None, description="A dynamic JSON object")


async def send_email(email: List[EmailStr]):
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>API Documentation Invitation</title>
        <style>
            .container {
                font-family: Arial, sans-serif;
                max-width: 600px;
                margin: auto;
                padding: 20px;
                border: 1px solid #e2e2e2;
                border-radius: 10px;
                background-color: #f9f9f9;
            }
            .header {
                background-color: #007bff;
                color: white;
                padding: 10px;
                text-align: center;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
            }
            .button {
                display: block;
                width: 200px;
                margin: 20px auto;
                padding: 10px;
                text-align: center;
                background-color: #007bff;
                color: white;
                text-decoration: none;
                border-radius: 5px;
            }
            .footer {
                text-align: center;
                margin-top: 20px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>API Documentation Invitation</h1>
            </div>
            <p>Hello,</p>
            <p>I am excited to invite you to view my User Management API documentation on <strong>ReDoc</strong>.</p>
            <p>You can access the documentation by clicking the button below:</p>
            <a href="https://github.com/fenilfaldu/FASTAPI_SQLALCHEMY" style="color: white;" class="button">View Source Code</a>
            Detailed document and output images are uploaded in Readme.md file on github

            <a href="http://ec2-44-220-145-197.compute-1.amazonaws.com:8080/redoc" style="color: white;" class="button">View API Redoc Documentation</a>
            <a href="http://ec2-44-220-145-197.compute-1.amazonaws.com:8080/docs" style="color: white;" class="button">View API Swagger UI</a>
            <p>I have Deployed FastAPI Application with SQLAlchemy on EC2 using Docker with RDS(Postgre sql) setup on AWS</p>
            <p>I appreciate your time and look forward to your feedback.</p>
            <div class="footer">
                <p>Thank you,<br>Faldu Fenil</p>
                <p>If you have any questions, feel free to reply to this email.</p>
            </div>
        </div>
    </body>
    </html>
    """

    message = MessageSchema(
        subject="API Documentation Invitation",
        recipients=email, 
        body=html,
        subtype="html"
    )

    fm = FastMail(conf)
    await fm.send_message(message)

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

@app.post("/send-invitation/")
async def send_invitation(background_tasks: BackgroundTasks):
    recipients = ["shraddha@aviato.consulting","pooja@aviato.consulting","prijesh@aviato.consulting","hiring@aviato.consulting"]
    background_tasks.add_task(send_email, recipients)
    return {"message": "Invitation email has been sent"}

@app.patch("/update_users")
async def update_user(item: UpdateDynamicJSON, db: Session = Depends(get_db)):
    db_item = db.query(DynamicData).filter(DynamicData.id == item.id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="User not found")
    if item.data is not None:
        db_item.data = item.data
    db.commit()
    db.refresh(db_item)
    return {"id": db_item.id, "data": db_item.data}

@app.delete("/delete_user/{user_id}")
async def delete_user(user_id: uuid.UUID, db: Session = Depends(get_db)):
    db_item = db.query(DynamicData).filter(DynamicData.id == user_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_item)
    db.commit()
    return {"message": "User deleted successfully"}

if __name__ == "__main__":
    config = uvicorn.Config(app=app, host="0.0.0.0", port=8080)
    server = uvicorn.Server(config)
    server.run()
