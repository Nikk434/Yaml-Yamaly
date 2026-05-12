import socketio

# sio = socketio.AsyncServer(
#     async_mode="asgi",
#     cors_allowed_origins="*",
# )

# socket_app = socketio.ASGIApp(
#     sio,
#     socketio_path="/ws/socket.io"
# )

# @sio.event
# async def join_room(sid, data):
#     session_token = data.get("session_token")
#     room_code = data.get("room_code")

#     if not session_token or not room_code:
#         return

#     db = SessionLocal()

#     session = (
#         db.query(Session)
#         .join(Room)
#         .filter(
#             Session.session_token == session_token,
#             Room.room_code == room_code
#         )
#         .first()
#     )

#     if not session:
#         db.close()
#         return

#     session.socket_sid = sid
#     session.last_seen_at = datetime.utcnow()
#     db.commit()

#     await sio.enter_room(sid, room_code)
#     await emit_room_counts(db, session.room_id, room_code)

#     db.close()

from fastapi import FastAPI
import socketio
from socket_server import sio
from socket_events import register_socket_events

fastapi_app = FastAPI()

# register events
register_socket_events(sio)

socket_app = socketio.ASGIApp(
    sio,
    other_asgi_app=fastapi_app
)

def make_socket_app(fastapi_app):
    return socketio.ASGIApp(sio, other_asgi_app=fastapi_app)