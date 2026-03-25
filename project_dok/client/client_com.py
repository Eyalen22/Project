import ctypes
import socket
import threading
import sys
from pubsub import pub
import queue
import time
import os
from operator import index

from actions import client_protocol
from shared.asymmetric_cypher import AsymmetricCipher
from shared.symmetric_cypher import SymmetricCipher

class ClientCommunication:

    def __init__(self, server_ip, port):
        self.my_socket = None
        self.server_ip = server_ip
        self.port = port
        self.cipher = None
        self.is_connected = False
        # pub.subscribe(self._close_socket, "close_client")
        threading.Thread(target=self._mainLoop, daemon=False).start()

    def _mainLoop(self):
        while True:
            while not self.is_connected:
                self._close_socket()
                try:
                    print(f"[*] Trying to connect to {self.server_ip}:{self.port}...")
                    self.my_socket = socket.socket()
                    self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    self.my_socket.connect((self.server_ip, self.port))
                    if self.my_socket:
                        print("[V] Connected & Encrypted. Waiting for data...")
                        self._change_key()
                    else:
                        print("[-] Key exchange failed.")
                except (socket.error, Exception) as e:
                    print(f"[-] Connection failed: {e}")

            time.sleep(1.0)

    def _change_key(self):
        """
        get's the same key as the server
        """
        server_pub_key = None
        try:
            len_pub = int(self.my_socket.recv(4).decode())
            server_pub_key = self.my_socket.recv(len_pub).decode()
        except Exception as e:
            print(f"Error during key exchange: {e}")
            self.my_socket.close()
            self.is_connected = False
        else:
            new_key = SymmetricCipher.random_symmetric_key()
            encrypted_key = AsymmetricCipher.encrypt(server_pub_key, new_key)
            try:
                self.my_socket.send(str(len(encrypted_key)).zfill(4).encode())
                self.my_socket.send(encrypted_key)
            except Exception as e:
                print(f"Error during key exchange: {e}")
                self.my_socket.close()
                self.is_connected = False
            else:
                self.cipher = SymmetricCipher(new_key)
                print(f"Key exchange successful. Encryption is active. - {new_key}")
                print(self.cipher)
                self.is_connected = True

    def _close_socket(self):
        """ סגירה יסודית ללא sys.exit """
        self.cipher = None
        self.is_connected = False
        if self.my_socket:
            self.my_socket.close()

    def send_msg(self, msg):
        """
        send a msg to the server
        :param msg:str
        :return:None
        """
        if self.cipher:
            new_msg = self.cipher.encrypt(msg.encode('utf-8'))
            len_msg = int.to_bytes(len(new_msg), 4, "big")
            print(len_msg , new_msg)
            try:
                self.my_socket.send(len_msg)
                self.my_socket.send(new_msg)
            except Exception as e:
                print(f"error in sending - {e}")
                self.is_connected = False
        return self.is_connected

    def send_file(self, file_name, path, user_name):
        """
        send details to the server + call _recv_file
        """
        file_path = os.path.join(path, file_name)
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                data = f.read()
            file_size = len(data)
            drive = os.path.splitdrive(path)
            new_path = self.replace_drive_with_name(path, self.get_drive_name(drive[0]))
            packed_msg = client_protocol.pack_back_up("03", file_name, new_path, file_size, user_name)
            if self.send_msg(packed_msg):
                try:
                    self.my_socket.sendall(self.cipher.encrypt(data))
                except Exception as e:
                    print(f"Client error during stream: {e}")
                    self.is_connected = False
        return self.is_connected

    def get_drive_name(self, drive_letter):
        drive_path = f"{drive_letter.strip(':')}:\\"
        volumeNameBuffer = ctypes.create_unicode_buffer(1024)
        ctypes.windll.kernel32.GetVolumeInformationW(
            ctypes.c_wchar_p(drive_path),
            volumeNameBuffer,
            ctypes.sizeof(volumeNameBuffer),
            None, None, None, None, 0
        )
        return volumeNameBuffer.value

    def replace_drive_with_name(self, full_path, volume_name):
        drive, rest_of_path = os.path.splitdrive(full_path)

        if drive:
            new_path = f"{volume_name}:{rest_of_path}"
            return new_path

        return full_path


if __name__ == '__main__':
    myQ = queue.Queue()
    myComm = ClientCommunication("127.0.0.1", 2222)
    for _ in range(100):
        print("mkjhjkh")



    # print("[!] Client started. Press Ctrl+C to stop.")
    # try:
    #     while True:
    #         index = input("press 1\n")
    #         if index == "1":
    #             myComm.send_msg("hi man")
    #         time.sleep(1)
    # except KeyboardInterrupt:
    #     print("\nExiting...")


