from shared import symmetric_cypher
import hashlib


def create_key(user_name, password):
    new_password = password[::-1]
    print(new_password)
    get_key = f"{user_name[2:]}{new_password}ido_vz"
    key_full_hash = hashlib.sha256(get_key.encode()).digest()
    key = key_full_hash[:32]
    print(key)

    return key


if __name__ == '__main__':
    user_name = input("user ->\n")
    password = input("password -> \n")
    key = create_key(user_name, password)

    cipher = symmetric_cypher.SymmetricCipher(key)

    with open("E:\Project\project_dok\server\\noam\E\\tevel.jpg", 'rb') as f:
        file_data = f.read()
        data = cipher.decrypt(file_data)

    with open("E:\Project\project_dok\server\\noam\E\\tevel.jpg", 'wb') as f:
        file_data = f.write(data)


