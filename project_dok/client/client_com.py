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

    def __init__(self, server_ip, port, recvQ):
        self.my_socket = None
        self.server_ip = server_ip
        self.port = port
        self.recvQ = recvQ
        self.cipher = None
        self.is_connected = False
        #pub.subscribe(self._close_socket, "get_out") - למחוק?

        threading.Thread(target=self._mainLoop, daemon=True).start()

    def _mainLoop(self):
        while True:
            self._close_socket()
            try:
                print(f"[*] Trying to connect to {self.server_ip}:{self.port}...")
                self.my_socket = socket.socket()
                self.my_socket.connect((self.server_ip, self.port))
                if self.my_socket:
                    print("[V] Connected & Encrypted. Waiting for data...")
                    self._change_key()
                    self.is_connected = True
                    while self.is_connected:
                        pass
                else:
                    print("[-] Key exchange failed.")

            except (socket.error, Exception) as e:
                print(f"[-] Connection failed: {e}")

            # 5. אם הגענו לכאן, החיבור נפל או לא הצליח. מחכים ומנסים שוב.
            print("[*] Sleeping 5 seconds before retrying...")
            time.sleep(5)

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
        if server_pub_key:
            new_key = SymmetricCipher.random_symmetric_key()
            encrypted_key = AsymmetricCipher.encrypt(server_pub_key, new_key)
            try:
                self.my_socket.send(str(len(encrypted_key)).zfill(4).encode())
                self.my_socket.send(encrypted_key)
            except Exception as e:
                print(f"Error during key exchange: {e}")
                self.my_socket.close()

            self.cipher = SymmetricCipher(new_key)
            print(f"Key exchange successful. Encryption is active. - {new_key}")
            print(self.cipher)
        else:
            print("error")

    def _close_socket(self):
        """ סגירה יסודית ללא sys.exit """
        self.cipher = None
        self.is_connected = False
        if self.my_socket:
            try:
                self.my_socket.shutdown(socket.SHUT_RDWR)
                self.my_socket.close()
            except:
                pass
            finally:
                self.my_socket = None

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

    def send_file(self, file_name, path, user_name):
        """
        send details to the server + call _recv_file
        """
        file_path = os.path.join(path, file_name)
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                data = f.read()
            file_size = len(data)
            packed_msg = client_protocol.pack_back_up("03", file_name, path, file_size, user_name)
            self.send_msg(packed_msg)
            try:
                self.my_socket.sendall(self.cipher.encrypt(data))
            except Exception as e:
                print(f"Client error during stream: {e}")
                self.is_connected = False

    def get_is_connection(self):
        return self.is_connected



if __name__ == '__main__':
    myQ = queue.Queue()
    myComm = ClientCommunication("127.0.0.1", 2222, myQ)

    print("[!] Client started. Press Ctrl+C to stop.")

    # לולאה אינסופית ב-main כדי שהתוכנית לא תיסגר!
    try:
        while True:
            index = input("press 1\n")
            if index == "1":
                myComm.send_msg("hi man")

            time.sleep(1)  # לא לצרוך 100% מעבד
    except KeyboardInterrupt:
        print("\nExiting...")


