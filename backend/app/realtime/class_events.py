from socket_server import sio

async def emit_class_created(room_code: str, obj):
    await sio.emit(
        "class_created",
        {
            "id": str(obj.id),
            "raw_class_name": obj.raw_class_name,
            "status": obj.status.value,
            "review_reason": obj.review_reason,
        },
        room=room_code
    )


async def emit_class_reviewed(room_code: str, obj):
    await sio.emit(
        "class_reviewed",
        {
            "id": str(obj.id),
            "status": obj.status.value,
            "review_reason": obj.review_reason,
        },
        room=room_code
    )
