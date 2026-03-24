import queue
from design.App import AppStand
import stand_com
import stand_protocol
from stand_com import StandCommunication
from pubsub import pub

class StandLogic:

    def __init__(self):
        self.msgQ = queue.Queue()
        self.designQ = queue.Queue()
        self.stand_com = stand_com.StandCommunication("127.0.0.1",2222, self.msgQ)
        pub.subscribe(self.get_msg, "got_msg")

    def handle_msg(self):
        pass

    def sign_in(self, user_name, password, mail):
        self.stand_com.send_msg(stand_protocol.pack_sigh_in(opcode="00", user_name=user_name, password=password, mail=mail))

    def log_in(self, user_name, password):
        self.stand_com.send_msg(stand_protocol.pack_log_in(opcode= "01", user_name=user_name, password=password))

    def add_dok(self, user_name, dok_name):
        self.stand_com.send_msg(stand_protocol.pack_add_dok(opcode="06", user_name=user_name, dok_path=dok_name))

    def restore(self, user_name, dok_name):
        self.stand_com.send_msg(stand_protocol.pack_restore(opcode="04", user_name=user_name, dok_path=dok_name))


    #temperery#
    def get_msg(self, msg):
        print(msg)

if __name__ == '__main__':
    stand_logic = StandLogic()
    AppStand(stand_logic.designQ)
