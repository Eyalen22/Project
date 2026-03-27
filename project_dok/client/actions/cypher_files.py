import base64
from shared import symmetric_cypher
import hashlib
import os

def create_key(user_name, password):
    """Generates a consistent 32-byte encryption key derived from user credentials and a custom salt"""
    # Reverse password and add salt for unique key derivation
    new_password = password[::-1]
    get_key = f"{user_name[2:]}{new_password}ido_vz"
    key_full_hash = hashlib.sha256(get_key.encode()).digest()
    key = key_full_hash[:32]
    return symmetric_cypher.SymmetricCipher(key)

def encrypt_file(file_path, key):
    """Encrypts the binary content of a file in-place using the provided symmetric key"""
    with open(file_path, 'rb') as f:
        file_data = f.read()
        data = key.encrypt(file_data)

    with open(file_path, 'wb') as f:
        f.write(data)

def encrypt_file_name(file_path, key):
    """Encrypts the file's name and renames it to a base64-encoded string to hide metadata on the drive"""
    directory = os.path.dirname(file_path)
    old_name = os.path.basename(file_path)
    encrypted_bytes = key.encrypt(old_name.encode())
    # Use URL-safe base64 to avoid illegal filename characters
    safe_name = base64.urlsafe_b64encode(encrypted_bytes).decode()
    new_path = os.path.join(directory, safe_name)

    if not os.path.exists(new_path):
        try:
            os.rename(file_path, new_path)
        except OSError:
            pass

def decrypt_file(file_path, key):
    """Restores the original binary content of an encrypted file"""
    with open(file_path, 'rb') as f:
        file_data = f.read()
        data = key.decrypt(file_data)
    with open(file_path, 'wb') as f:
        f.write(data)

def decrypt_file_name(file_path, key):
    """Decodes the base64 filename and decrypts it back to its original human-readable name"""
    directory = os.path.dirname(file_path)
    old_name = os.path.basename(file_path)
    try:
        encrypt_bytes = base64.urlsafe_b64decode(old_name.encode())
        original_name = key.decrypt(encrypt_bytes).decode()
        new_path = os.path.join(directory, original_name)

        if not os.path.exists(new_path):
            os.rename(file_path, new_path)
    except Exception:
        pass

if __name__ == '__main__':
    # Standalone encryption test
    u_name = input("Enter username: ")
    pwd = input("Enter password: ")
    path = r"F:\test_image.jpg"
    cipher_key = create_key(u_name, pwd)
    encrypt_file(file_path=path, key=cipher_key)
    print("Encryption test completed.")