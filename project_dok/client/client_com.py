import socket
import threading
import sys
import queue
import time
import os
import client_protocol
from shared.asymmetric_cypher import AsymmetricCipher
from shared.symmetric_cypher import SymmetricCipher

class ClientCommunication:


    def __init__(self, server_ip, port, recvQ):
        self.my_socket = socket.socket()
        self.server_ip = server_ip
        self.port = port
        self.recvQ = recvQ
        self.cipher = None

        threading.Thread(target=self._mainLoop).start()

    def _mainLoop(self):

        try:
            self.my_socket.connect((self.server_ip, self.port))
        except Exception as e:
            print(f"error in connecting - {e}")
            sys.exit("server not currently available - try later")

        self._change_key()


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


    def _client_close(self):
        """
        closing socket
        :return: None
        """
        self.my_socket.close()
        sys.exit()

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
                self._client_close()

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
                self._client_close()


if __name__ == '__main__':
    myQ = queue.Queue()
    myComm = ClientCommunication("127.0.0.1", 1000, myQ)
    time.sleep(0.3)
    myComm.send_msg("hello man")
    myComm.send_file("ido.jpg", "E:\Project", "noam")
    myComm.send_file("tevel.jpg", "E:\\", "noam")


