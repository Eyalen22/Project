import threading
import dok_db
import server_com
import queue
import server_protocol
import os
class ServerLogic:

    def __init__(self):
        self.msgQ = queue.Queue()
        self.server_com = server_com.ServerCommunication(2222, self.msgQ)
        self.serverDB = dok_db.MyDB()
        self.commends = {"00": self.sign_in, "01": self.log_in, "04": self.restore, "06": self.add_dok, "07": self.get_doks_name}
        threading.Thread(target=self.handle_msg, daemon=True).start()

    def handle_msg(self):
        while True:
            ip, msg = self.msgQ.get()
            if msg:
                opcode , params = server_protocol.unpack(msg)
                self.commends[opcode](ip, params)


    def sign_in(self,ip, params):
        user_name , password, mail = params
        status = "01"
        if self.serverDB.add_user(username=user_name, password=password, mail=mail):
            status = "00"
        print(f"status is - {status} - sign in")
        self.server_com.send_msg(ip, server_protocol.pack_status("00", status))

    def log_in(self,ip, params):
        user_name , password = params
        status = "01"
        if self.serverDB.user_exist(user_name, password):
            status = "00"
        print(f"status is - {status} - log in")
        self.server_com.send_msg(ip, server_protocol.pack_status("01", status))

    def add_dok(self,ip, params):
        user_name, dok_name = params
        mail = ""
        status = "01"
        if self.serverDB.user_dok_match(user_name=user_name, dok_name=dok_name) or self.serverDB.add_dok(username= user_name, dok_name=dok_name):
            status = "00"
            mail = self.serverDB.get_mail(user_name=user_name)
        print(f"status is - {status} - add dok")
        self.server_com.send_msg(ip, server_protocol.pack_add_dok("06", status, mail))

    def get_doks_name(self,ip , params):
        user_name = params[0]
        list_of_doks = self.serverDB.get_user_doks(username=user_name)
        msg_to_send = "@#".join(list_of_doks)
        print(msg_to_send)
        self.server_com.send_msg(ip, server_protocol.pack_get_doks_name("07", msg_to_send))

    def restore(self, ip, params):
        user_name, dok_name = params
        if self.serverDB.user_dok_match(user_name=user_name, dok_name=dok_name):
            base_path = r"E:\Project\project_dok\server"
            abs_search_path = os.path.join(base_path, user_name, dok_name)
            if not os.path.exists(abs_search_path):
                print(f"Error: Folder {abs_search_path} not found!")
                self.server_com.send_msg(ip, server_protocol.pack_status("11", "01"))
                return
            print(f"Starting restore for {user_name}...")
            for root, dirs, files in os.walk(abs_search_path):
                for file_name in files:
                    relative_path = os.path.relpath(root, base_path)
                    self.server_com.send_file(file_name=file_name, path=relative_path, client_ip=ip)
            print("restored successfully")
            self.server_com.send_msg(ip, server_protocol.pack_status("11", "00"))
        else:
            self.server_com.send_msg(ip, server_protocol.pack_status("11", "01"))


if __name__ == '__main__':
    server_logic = ServerLogic()