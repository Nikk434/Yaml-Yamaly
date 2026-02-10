import secrets

ROOM_CODE_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%&*"
ROOM_CODE_LENGTH = 6

def generate_room_code() -> str:
    return "".join(
        secrets.choice(ROOM_CODE_CHARS)
        for _ in range(ROOM_CODE_LENGTH)
    )

def generate_owner_secret() -> str:
    return secrets.token_urlsafe(48)
