import socket
import threading
import sys
import queue
import time
import os
from pathlib import Path
import stand_protocol
from shared.asymmetric_cypher import AsymmetricCipher
from shared.symmetric_cypher import SymmetricCipher

class StandCommunication:


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
                encrypt_msg = self.my_socket.recv(long)
            except Exception as e:
                print(f"error in receiving - {e}")
                self._client_close()
                break
            msg = self.cipher.decrypt(encrypt_msg).decode()
            if not msg[0:2] == "04":
                self.recvQ.put(msg)
            else:
                self._recv_file(msg)


    def _recv_file(self, msg):
        opcode, parts = stand_protocol.unpack(msg)
        if not parts[2].isdigit():
            self._client_close()
        else:
            file_size = int(parts[2])
            data = bytearray()
            while len(data) < file_size:
                toRead = file_size - len(data)
                if toRead > 1024:
                    try:
                        data.extend(self.my_socket.recv(1024))
                    except Exception as e:
                        break
                else:
                    try:
                        data.extend(self.my_socket.recv(toRead))
                    except Exception as e:
                        break
                    else:
                        break

            if not len(data) == file_size:
                self._client_close()

            else:
                decrypt_data = self.cipher.decrypt(data)
                clean_path = parts[1].replace(":", "")
                downloads_path = str(Path.home() / "Downloads")

                full_directory = os.path.join(downloads_path, clean_path)
                full_file_path = os.path.join(full_directory, parts[0])
                os.makedirs(full_directory, exist_ok=True)

                with open(full_file_path, "wb") as f:
                    f.write(decrypt_data)
                print("New file saved to:", full_file_path)

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
            try:
                self.my_socket.send(len_msg)
                self.my_socket.send(new_msg)
            except Exception as e:
                print(f"error in sending - {e}")
                self._client_close()

if __name__ == '__main__':
    if __name__ == '__main__':
        myQ = queue.Queue()
        myComm = ClientCommunication("127.0.0.1", 1000, myQ)
        time.sleep(0.3)
        while True:
            pass


