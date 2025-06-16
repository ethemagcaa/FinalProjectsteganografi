from Crypto.Cipher import AES, DES, Blowfish
from Crypto.Util.Padding import pad, unpad

def get_cipher(key: bytes, algorithm: str):
    if algorithm == 'AES':
        return AES.new(key, AES.MODE_ECB)
    elif algorithm == 'DES':
        return DES.new(key, DES.MODE_ECB)
    elif algorithm == 'Blowfish':
        return Blowfish.new(key, Blowfish.MODE_ECB)
    else:
        raise ValueError("Unsupported algorithm")

def encrypt_image_bytes(data: bytes, key: str, algorithm: str) -> bytes:
    key_bytes = key.encode('utf-8')
    if algorithm == 'AES':
        key_bytes = key_bytes[:16]
    elif algorithm == 'DES':
        key_bytes = key_bytes[:8]
    elif algorithm == 'Blowfish':
        key_bytes = key_bytes[:16]
    cipher = get_cipher(key_bytes, algorithm)
    return cipher.encrypt(pad(data, cipher.block_size))

def decrypt_image_bytes(data: bytes, key: str, algorithm: str) -> bytes:
    key_bytes = key.encode('utf-8')
    if algorithm == 'AES':
        key_bytes = key_bytes[:16]
    elif algorithm == 'DES':
        key_bytes = key_bytes[:8]
    elif algorithm == 'Blowfish':
        key_bytes = key_bytes[:16]
    cipher = get_cipher(key_bytes, algorithm)
    return unpad(cipher.decrypt(data), cipher.block_size)
