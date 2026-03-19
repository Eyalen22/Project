import base64
from shared import symmetric_cypher
import hashlib
import os
import wx

def create_key(user_name, password):
    new_password = password[::-1]
    get_key = f"{user_name[2:]}{new_password}ido_vz"
    key_full_hash = hashlib.sha256(get_key.encode()).digest()
    key = key_full_hash[:32]
    cipher = symmetric_cypher.SymmetricCipher(key)

    return cipher

def encrypt_file(file_path, key):
    with open(file_path, 'rb') as f:
        file_data = f.read()
        data = key.encrypt(file_data)

    with open(file_path, 'wb') as f:
        f.write(data)



def encrypt_file_name(file_path, key):
    directory = os.path.dirname(file_path)
    old_name = os.path.basename(file_path)
    encrypted_bytes = key.encrypt(old_name.encode())
    safe_name = base64.urlsafe_b64encode(encrypted_bytes).decode()
    new_path = os.path.join(directory, safe_name)
    if not os.path.exists(new_path):
        try:
            os.rename(file_path, new_path)
        except OSError as e:
            pass


def decrypt_file(file_path, key):
    with open(file_path, 'rb') as f:
        file_data = f.read()
        data = key.decrypt(file_data)
    with open(file_path, 'wb') as f:
        f.write(data)



def decrypt_file_name(file_path, key):
    directory = os.path.dirname(file_path)
    old_name = os.path.basename(file_path)
    try:
        encrypt_bytes = base64.urlsafe_b64decode(old_name.encode())
        original_name = key.decrypt(encrypt_bytes).decode()
        new_path = os.path.join(directory, original_name)
        if not os.path.exists(new_path):
            os.rename(file_path, new_path)
    except Exception as e:
        pass


if __name__ == '__main__':
    user_name = input("user ->\n")
    password = input("password -> \n")
    file_path = r"F:\Project\project_dok\server\noam\E\tevel.jpg"
    key = create_key(user_name, password)
    encrypt_file(file_path=file_path, key=key)


