import queue
import threading
import threading
from design.App import AppStand
import stand_com
import stand_protocol
from stand_com import StandCommunication
from pubsub import pub
from shared import create_exe

class StandLogic:

    def __init__(self):
        self.msgQ = queue.Queue()
        self.designQ = queue.Queue()
        self.stand_com = stand_com.StandCommunication("127.0.0.1",2222, self.msgQ)
        self.temp_password = None
        self.temp_dok_path = None
        self.temp_user = None
        pub.subscribe(self.sign_in, "sign_in")
        pub.subscribe(self.log_in, "log_in")
        pub.subscribe(self.add_dok, "add_dok")
        threading.Thread(target=self.handle_msg, daemon=True).start()

    def handle_msg(self):
        while True:
            packed_msg = self.msgQ.get()
            opcode, msg = stand_protocol.unpack(packed_msg)
            if opcode == "11":
                print("time to restore")
            elif opcode == "06":
                status = msg[0]
                if status == "00":
                    # status = create_exe.run_full_process(self.temp_dok_path,
                    #                             self.temp_user,
                    #                             self.temp_password,
                    #                             msg[1])
                    print("start exe")
                else:
                    print("error")
                self.kill_temp()
                self.designQ.put(status)
            else:
                print(msg[0])
                self.designQ.put(msg[0])

    def sign_in(self, user_name, password, mail):
        self.stand_com.send_msg(stand_protocol.pack_sigh_in(opcode="00", user_name=user_name, password=password, mail=mail))

    def log_in(self, user_name, password):
        self.stand_com.send_msg(stand_protocol.pack_log_in(opcode= "01", user_name=user_name, password=password))

    def add_dok(self, user_name, password, dok_name, dok_path):
        self.stand_com.send_msg(stand_protocol.pack_add_dok(opcode="06", user_name=user_name, dok_path=dok_name))
        self.temp_password = password
        self.temp_user = user_name
        self.temp_dok_path = dok_path


    def restore(self, user_name, dok_name):
        self.stand_com.send_msg(stand_protocol.pack_restore(opcode="04", user_name=user_name, dok_path=dok_name))

    def kill_temp(self):
        self.temp_password = None
        self.temp_user = None
        self.temp_dok_path = None

    def restore_to_dok(self):
        pass

    def get_msg(self, msg):
        print(msg)

if __name__ == '__main__':
    stand_logic = StandLogic()
    AppStand(stand_logic.designQ)
