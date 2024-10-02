import base64

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

# AES-256 в режиме CBC
KEY = get_random_bytes(32)  # 32 байта = 256 бит


def encrypt_message(message: str) -> str:
    cipher = AES.new(KEY, AES.MODE_CBC)
    iv = cipher.iv  # Вектор инициализации
    encrypted_message = cipher.encrypt(
        pad(message.encode(), AES.block_size),
    )
    return base64.b64encode(iv + encrypted_message).decode(
        "utf-8",
    )


def decrypt_message(encrypted_message: str) -> str:
    print(encrypted_message)
    encrypted_message_bytes = base64.b64decode(encrypted_message)
    iv = encrypted_message_bytes[:16]  # Первые 16 байт — это IV
    encrypted_message_bytes = encrypted_message_bytes[
        16:
    ]  # Остальное — шифрованное сообщение
    cipher = AES.new(KEY, AES.MODE_CBC, iv)
    decrypted_message = unpad(
        cipher.decrypt(encrypted_message_bytes),
        AES.block_size,
    )  # Дешифруем и убираем padding
    return decrypted_message.decode("utf-8")
