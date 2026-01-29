import socket
import threading
import time

import select
import queue
import os

import server_protocol
from shared.asymmetric_cypher import AsymmetricCipher
from shared.symmetric_cypher import SymmetricCipher

class ServerCommunication:

    def __init__(self, port, recvQ):
        self.server_socket = socket.socket()
        self.port = port
        self.recvQ = recvQ
        self.asym_cipher = AsymmetricCipher()
        self.open_clients = {}      # [socket]:[ip, cipher]

        threading.Thread(target=self._mainLoop).start()

    def _mainLoop(self):
        self.server_socket.bind(('0.0.0.0', self.port))
        self.server_socket.listen(5)
        while True:
            rlist, wlist, xlist = select.select([self.server_socket]+ list(self.open_clients.keys()), list(self.open_clients.keys()), [], 0.01)
            for current_client in rlist:
                if current_client is self.server_socket:
                    (client_soc, addr) = self.server_socket.accept()
                    valid_ip = addr[0]
                    ip_list = addr[0].split('.')
                    if ip_list[0] == "127" and ip_list[1] == "0" and ip_list[2] == "0":
                        valid_ip = self.check_ip_values(addr[0])
                    print(f"{valid_ip} - connected to your server")
                    threading.Thread(target=self._change_key, args=(client_soc, valid_ip,)).start()
                else:
                    try:
                        long = int.from_bytes(current_client.recv(4), byteorder='big')
                        encrypt_msg = current_client.recv(long)
                    except Exception as e:
                        print(f"error in recv- {e}")
                        self._close_client(current_client)
                        print(f"client disconnected - {e}")
                    else:
                        msg = self.open_clients[current_client][1].decrypt(encrypt_msg).decode()
                        if not msg[0:2] == "03":
                            self.recvQ.put((self.open_clients[current_client][0], msg))
                        else:
                            self._recv_file(current_client, msg)



    def _change_key(self, client_soc, client_ip):
        """
        get's the same key as the client
        """
        public_key = self.asym_cipher.get_public_key()
        try:
            client_soc.send(str(len(public_key)).zfill(4).encode())
            client_soc.send(public_key)
            len_encrypted_key = int(client_soc.recv(4).decode())
            encrypted_key = client_soc.recv(len_encrypted_key)
        except Exception as e:
            print(f"Server Error during exchange - {e}")
        else:
            symmetric_key = self.asym_cipher.decrypt(encrypted_key)
            self.open_clients[client_soc] = [client_ip, SymmetricCipher(symmetric_key)]
            print(f"Server: Secure channel established with {client_ip} , {symmetric_key}")

    ## make pretty ##

    def _recv_file(self, client_soc, msg):

        opcode, parts =  server_protocol.unpack(msg)
        if not parts[2].isdigit():
            self._close_client(client_soc)
        else:
            file_size = int(parts[2])
            data = bytearray()
            while len(data) < file_size:
                toRead = file_size - len(data)
                if toRead > 1024:
                    try:
                        data.extend(client_soc.recv(1024))
                    except Exception as e:
                       break
                else:
                    try:
                        data.extend(client_soc.recv(toRead))
                    except Exception as e:
                       break
                    else:
                        break

            if not len(data) == file_size:
                self._close_client(client_soc)

            else:
                decrypt_data = self.open_clients[client_soc][1].decrypt(data)
                clean_path = parts[1].replace(":", "")
                full_directory = os.path.join(parts[3], clean_path)
                full_file_path = os.path.join(full_directory, parts[0])
                os.makedirs(full_directory, exist_ok=True)
                with open(full_file_path, "wb") as f:
                    f.write(decrypt_data)
                print("new file in: ", full_file_path)

    def _close_client(self, client_soc):
        """
        close the client
        :param client_socket:socket
        :return:None
        """
        if client_soc in self.open_clients.keys():
            print(f"{self.open_clients[client_soc]} - disconnect")
            del self.open_clients[client_soc]
            client_soc.close()

    def _get_socket_by_ip(self, client_ip):
        """
        giving the correct soc by the ip
        :param client_ip: str
        :return: return socket
        """
        soc = None
        for socket in self.open_clients:
            if client_ip == self.open_clients[socket][0]:
                soc = socket
                break

        return soc

    def close_client(self, client_ip):
        """
        closing the client
        :param client_ip: str
        :return: None
        """
        soc = self._get_socket_by_ip(client_ip)
        self._close_client(soc)

    def send_msg(self, client_ip, msg):
        """
        sending mag to the correct client by ip
        :param client_ip:str
        :param msg:str
        :return:None
        """
        soc = self._get_socket_by_ip(client_ip)
        if soc:
            key = self.open_clients[soc][1]
            new_msg = key.encrypt(msg.encode('utf-8'))
            msg_len = int.to_bytes(len(new_msg), 10, 'big')
            try:
                soc.send(msg_len)
                soc.send(new_msg)
            except Exception as e:
                print(f"error in sending - {e}")
                self._close_client(soc)


    def check_ip_values(self, ip:str) -> str:
        """

        :param ip:
        :return:
        """
        is_ip_exist = True
        if ip not in [client_info[0] for client_info in self.open_clients.values()]:
            print(f"ip is valid: {ip}")
            is_ip_exist = False

        i = 2
        while is_ip_exist:
            new_ip = ip.rsplit(".",1)[0] + "." + str(i)
            if new_ip not in [client_info[0] for client_info in self.open_clients.values()]:
                print(f"new ip: {new_ip}")
                is_ip_exist = False
                ip = new_ip
            i += 1

        return ip





if __name__ == '__main__':
    myQ = queue.Queue()
    myComm = ServerCommunication(1000, myQ)



    while True:
        hello = myQ.get()[1]
        if hello:
            print(f"{hello}")



