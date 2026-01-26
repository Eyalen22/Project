import socket
import threading
import select
import queue
import os
from shared.asymmetric_cypher import AsymmetricCipher
from shared.symmetric_cypher import SymmetricCipher

class ServerCommunication:

    def __init__(self, port, recvQ):
        self.server_socket = socket.socket()
        self.port = port
        self.recvQ = recvQ
        self.asym_cipher = AsymmetricCipher()
        self.open_client = {}
        self.boards = {}
        threading.Thread(target=self._mainLoop).start()

    def _mainLoop(self):
        self.server_socket.bind(('0.0.0.0', self.port))
        self.server_socket.listen(5)
        while True:
            rlist, wlist, xlist = select.select([self.server_socket] + list(self.open_client.keys()), list(self.open_client.keys()), [], 0.1)
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
                        msg = self.open_client[current_client][1].decrypt(encrypt_msg)
                    except Exception as e:
                        print(f"error in recv- {e}")
                        self._close_client(current_client)
                        print(f"client disconnected - {e}")
                    else:
                        try:
                            msg = msg.decode('utf-8')
                            parts = msg.split("@#2")
                            opcode = parts[0]
                            user_id = self.open_client[current_client][0]
                            if opcode == "03":
                                threading.Thread(target=self._recv_file, args=(current_client, parts)).start()
                            else:
                                self.recvQ.put((user_id, msg))
                        except Exception as e:
                            print(f"error in decodeing- {e}")


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
            iv = client_soc.recv(16)
        except Exception as e:
            print(f"Server Error during exchange - {e}")
        else:
            symmetric_key = self.asym_cipher.decrypt(encrypted_key)
            self.open_client[client_soc] = [client_ip, SymmetricCipher(symmetric_key, iv)]

            print(f"Server: Established secure channel with {client_ip} - {symmetric_key}")

    def _recv_file(self, client_soc, details):
        """
        client_soc: הסוקט של הלקוח הנוכחי
        details: [opcode, file_name, original_path, file_len, user_name]
        """
        try:
            cipher = self.open_client[client_soc][1]

            file_name = details[1]
            file_size = int(details[3])
            user_name = details[4]
            user_temp_path = os.path.join("temp_folder", user_name)
            if not os.path.exists(user_temp_path):
                os.makedirs(user_temp_path)
            full_path = os.path.join(user_temp_path, file_name)
            print(f"Server receiving file from {user_name}...")
            remaining_data = file_size
            with open(full_path, 'wb') as f:
                while remaining_data > 0:
                    chunk_size = min(1024, remaining_data)
                    chunk = client_soc.recv(chunk_size)
                    if not chunk:
                        break
                    decrypted_chunk = cipher.decrypt(chunk)
                    f.write(decrypted_chunk)
                    remaining_data -= len(decrypted_chunk)
            print(f"File saved successfully at: {full_path}")
            logic_msg = f"03@#2{file_name}@#2{details[2]}@#2{user_name}@#2{full_path}"
            self.recvQ.put((self.open_client[client_soc][0], logic_msg))
        except Exception as e:
            print(f"Error in server _recv_file: {e}")

    def _close_client(self, client_soc):
        """
        close the client
        :param client_socket:socket
        :return:None
        """
        if client_soc in self.open_client.keys():
            print(f"{self.open_client[client_soc]} - disconnect")
            del self.open_client[client_soc]
            client_soc.close()

    def get_socket_by_ip(self, client_ip):
        """
        giving the correct soc by the ip
        :param client_ip: str
        :return: return socket
        """
        soc = None
        for socket in self.open_client:
            if client_ip == self.open_client[socket][0]:
                soc = socket
                break

        return soc

    def close_client(self, client_ip):
        """
        closing the client
        :param client_ip: str
        :return: None
        """
        soc = self.get_socket_by_ip(client_ip)
        self._close_client(soc)

    def send_msg(self, client_ip, msg):
        """
        sending mag to the correct client by ip
        :param client_ip:str
        :param msg:str
        :return:None
        """
        soc = self.get_socket_by_ip(client_ip)
        if soc:
            key = self.open_client[soc][1]
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
        if ip not in [client_info[0] for client_info in self.open_client.values()]:
            print(f"ip is valid: {ip}")
            is_ip_exist = False

        i = 2
        while is_ip_exist:
            new_ip = ip.rsplit(".",1)[0] + "." + str(i)
            if new_ip not in [client_info[0] for client_info in self.open_client.values()]:
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



