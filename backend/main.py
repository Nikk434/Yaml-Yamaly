from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# from app.db.base import Base
from app.db.base import Base
from app.api.room import create_room_endpoint
from app.db.session import engine
from app.api.room import router as room_router
from app.models.room import Room
from app.models.session import Session, SessionRole
from app.schemas.room import JoinRoomRequest, JoinRoomResponse

app = FastAPI()
Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8080", "http://127.0.0.1:8080"],  # Add your frontend URLs
    allow_credentials=True,  # THIS IS THE KEY LINE - allows cookies
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(room_router)