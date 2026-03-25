import threading
import dok_db
import server_com
import queue
import server_protocol

class ServerLogic:

    def __init__(self):
        self.msgQ = queue.Queue()
        self.server_com = server_com.ServerCommunication(2222, self.msgQ)
        self.serverDB = dok_db.MyDB()
        self.commends = {"00": self.sign_in, "01": self.log_in, "06": self.add_dok}
        threading.Thread(target=self.handle_msg, daemon=True).start()

    def handle_msg(self):
        while True:
            ip, msg = self.msgQ.get()
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
        if self.serverDB.add_dok(username= user_name, dok_name=dok_name):
            status = "00"
            mail = self.serverDB.get_mail(user_name=user_name)
        print(f"status is - {status} - add dok")
        self.server_com.send_msg(ip, server_protocol.pack_add_dok("06", status, mail))

if __name__ == '__main__':
    server_logic = ServerLogic()