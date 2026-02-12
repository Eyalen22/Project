from shared import symmetric_cypher
import hashlib
import os

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

    # directory = os.path.dirname(file_path)
    # old_name = os.path.basename(file_path)
    # encrypted_name = key.encrypt(old_name.encode())
    # new_path = os.path.join(directory, encrypted_name.decode())
    # os.rename(file_path, new_path)


def decrypt_file(file_path, key):
    with open(file_path, 'rb') as f:
        file_data = f.read()
        data = key.decrypt(file_data)

    with open(file_path, 'wb') as f:
        f.write(data)

    # directory = os.path.dirname(file_path)
    # old_name = os.path.basename(file_path)
    # encrypted_name = key.decrypt(old_name.encode())
    # new_path = os.path.join(directory, encrypted_name.decode())
    # os.rename(file_path, new_path)



if __name__ == '__main__':
    user_name = input("user ->\n")
    password = input("password -> \n")
    file_path = r"F:\Project\project_dok\server\noam\E\tevel.jpg"
    key = create_key(user_name, password)
    encrypt_file(file_path=file_path, key=key)


