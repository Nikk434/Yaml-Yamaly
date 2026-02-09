import secrets
import string


ROOM_CODE_CHARS = "!@#$*abcdefghijklmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ1234567890"

def generate_room_code(length: int = 6) -> str:
    return "".join(secrets.choice(ROOM_CODE_CHARS) for _ in range(length))


def generate_host_token() -> str:
    # 256-bit token
    return secrets.token_hex(32)
