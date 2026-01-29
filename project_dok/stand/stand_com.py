import socket
import threading
import sys
import queue
import time
import os
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

        while True:
            try:
                long = int.from_bytes(self.my_socket.recv(10), "big")
                msg = self.my_socket.recv(long)
                new_msg = self.cipher.decrypt(msg).decode()
                parts = new_msg.split("@#2")
                opcode = parts[0]
                if opcode == "04":
                    self._recv_file(parts)
                else:
                    self.recvQ.put(new_msg)

            except Exception as e:
                print(f"error in receiving - {e}")
                self._client_close()
                break

    def _recv_file(self, details):
        """
        details: [opcode, file_name, file_path, file_len]
        """
        file_name = details[1]
        try:
            file_size = int(details[3])
        except:
            print("Error: Invalid file size")
            return
        try:
            if not os.path.exists("downloads"):
                os.makedirs("downloads")
            full_path = os.path.join("downloads", file_name)
            print(f"Receiving file: {file_name}...")
            remaining_data = file_size
            with open(full_path, 'wb') as f:
                while remaining_data > 0:
                    chunk_size = min(1024, remaining_data)
                    chunk = self.my_socket.recv(chunk_size)
                    if not chunk:
                        break
                    if self.cipher:
                        chunk = self.cipher.decrypt(chunk)
                    f.write(chunk)
                    remaining_data -= len(chunk)
            msg_for_queue = "@#2".join(details) + f"@#2{full_path}"
            self.recvQ.put(msg_for_queue)
            print(f"File saved and path sent to logic: {full_path}")
        except Exception as e:
            print(f"Error in _recv_file: {e}")


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

if __name__ == '__main__':
    myQ = queue.Queue()
    myComm = ClientCommunication("127.0.0.1", 1000, myQ)
    time.sleep(0.3)

    myComm.send_msg("hello barak, "*100 + " - hey man")


