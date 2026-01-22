import socket
import threading
import sys
import queue
import time
from shared.asymmetric_cypher import AsymmetricCipher
from shared.symmetric_cypher import SymmetricCipher

class ClientCommunication:


    def __init__(self, server_ip, port, recvQ):
        self.my_socket = socket.socket()
        self.server_ip = server_ip
        self.port = port
        self.recvQ = recvQ
        self.iv = SymmetricCipher.random_iv()
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
            new_iv = SymmetricCipher.random_iv()
            encrypted_key = AsymmetricCipher.encrypt(server_pub_key, new_key)
            try:
                self.my_socket.send(str(len(encrypted_key)).zfill(4).encode())
                self.my_socket.send(encrypted_key)
                self.my_socket.send(new_iv)
            except Exception as e:
                print(f"Error during key exchange: {e}")
                self.my_socket.close()

            self.cipher = SymmetricCipher(new_key, new_iv)
            self.iv = new_iv
            print(f"Key exchange successful. Encryption is active. - {new_key}")
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
            try:
                self.my_socket.send(len_msg)
                self.my_socket.send(new_msg)
            except Exception as e:
                print(f"error in sending - {e}")
                self._client_close()



    def send_file(self, file_name, path, file_len, user_name):
        pass

    def _send_file(self):
        pass


if __name__ == '__main__':
    myQ = queue.Queue()
    myComm = ClientCommunication("127.0.0.1", 1000, myQ)
    time.sleep(0.3)

    myComm.send_msg("hello barak"*100 + " - hey man")


