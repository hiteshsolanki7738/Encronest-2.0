from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Hash import SHA256

BLOCK_SIZE = 16  # AES block size


# ---------------------------
# Generate AES-256 key from password
# ---------------------------
def derive_key(password: str) -> bytes:
    return SHA256.new(password.encode()).digest()


# ---------------------------
# Padding helpers (SAFE)
# ---------------------------
def pad(data: bytes) -> bytes:
    pad_len = BLOCK_SIZE - len(data) % BLOCK_SIZE
    return data + bytes([pad_len] * pad_len)


def unpad(data: bytes) -> bytes:
    pad_len = data[-1]

    # Safety check
    if pad_len < 1 or pad_len > BLOCK_SIZE:
        raise ValueError("Invalid padding")

    return data[:-pad_len]


# ---------------------------
# Encrypt file
# ---------------------------
def encrypt_file(input_path: str, output_path: str, password: str):
    try:
        key = derive_key(password)
        iv = get_random_bytes(16)
        cipher = AES.new(key, AES.MODE_CBC, iv)

        with open(input_path, "rb") as f:
            plaintext = f.read()

        ciphertext = cipher.encrypt(pad(plaintext))

        with open(output_path, "wb") as f:
            f.write(iv + ciphertext)

        return True

    except Exception as e:
        print("Encryption Error:", e)
        return False


# ---------------------------
# Decrypt file
# ---------------------------
def decrypt_file(encrypted_bytes: bytes, password: str) -> bytes:
    try:
        key = derive_key(password)

        if len(encrypted_bytes) < 16:
            raise ValueError("Invalid encrypted file")

        iv = encrypted_bytes[:16]
        ciphertext = encrypted_bytes[16:]

        cipher = AES.new(key, AES.MODE_CBC, iv)
        plaintext = cipher.decrypt(ciphertext)

        return unpad(plaintext)

    except Exception as e:
        raise ValueError("Wrong password or corrupted file")