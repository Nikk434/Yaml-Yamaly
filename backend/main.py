from fastapi import FastAPI

from app.api import rooms
# from app.api import create_room
from app.db.sessions import engine
from app.db.base import Base
from app.api import sessions

app = FastAPI(
    title="YOLO Class Mapping Tool",
    version="0.1.0"
)

# Create tables (only for dev / internal tool)
Base.metadata.create_all(bind=engine)

# Routers
app.include_router(
    rooms.router,
    prefix="/api",
    tags=["rooms"]
)
app.include_router(sessions.router, prefix="/api")
