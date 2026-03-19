from operator import index
from client.actions import cypher_files
import try_exe
import os
import string
import sys

users = {"ido": "12345", "noam": "eyal_en22"}


def get_files(drive_letter):
    file_paths = []
    current_executable = os.path.basename(sys.executable if getattr(sys, 'frozen', False) else __file__)
    excluded_names = {current_executable, "OPEN_DOK.exe", "client_logic.exe", "desktop.ini", "logs.log"}
    for root, dirs, files in os.walk(drive_letter, topdown=False):
        for file in files:
            if file.endswith(".exe") or file in excluded_names or file.startswith('.'):
                continue

            full_path = os.path.join(root, file)
            file_paths.append(full_path)
    return file_paths


def get_drive_list():
    # בודק לכל אות באלף-בית (A-Z) אם הנתיב שלה קיים
    drives = [f"{letter}:\\" for letter in string.ascii_uppercase if os.path.exists(f"{letter}:\\") ]
    return drives


if __name__ == '__main__':
    dok = ""
    user_name = ""
    password = ""
    user = False
    get_drives = get_drive_list()
    print("ready to start add DOK to your computer")

    while True:
        add_dok = get_drive_list()
        for i in add_dok:
            if i not in get_drives:
                dok = i
                break
        if dok:
            break

    index = input(
        "press the number for action:\n1 - put inside your dok the server files\n2 - decrypt your DOK\n3 - encrypt your DOK\n-> ")
    if not index == "1":
        while not user:
            user_name = input("enter your user name ->")
            password = input("enter your password -> ")
            if user_name in users.keys() and users[user_name] == password:
                user = True
            else:
                print("wrong user name or password\n")
    while True:
        if index == "1":
            user_name, password = try_exe.run_full_process(dok)
            key = cypher_files.create_key(user_name=user_name, password=password)
            files = get_files(dok)
            for i in files:
                cypher_files.encrypt_file(file_path=i, key=key)
                cypher_files.encrypt_file_name(file_path=i, key=key)
        elif index == "2":
            if user_name in users.keys() and users[user_name] == password:
                key = cypher_files.create_key(user_name=user_name, password=password)
                files = get_files(dok)
                for i in files:
                    cypher_files.decrypt_file(file_path=i, key=key)
                    cypher_files.decrypt_file_name(file_path=i, key=key)
        elif index == "3":
            if user_name in users.keys() and users[user_name] == password:
                key = cypher_files.create_key(user_name=user_name, password=password)
                files = get_files(dok)
                for i in files:
                    cypher_files.encrypt_file(file_path=i, key=key)
                    cypher_files.encrypt_file_name(file_path=i, key=key)

        index = input(
            "press the number for action:\n1 - put inside your dok the server files\n2 - decrypt your DOK\n3 - encrypt your DOK\n-> ")
