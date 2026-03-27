import os
import queue
import shutil
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
        """Initializes queues, communication settings, and subscribes to system events"""
        self.msgQ = queue.Queue()
        self.designQ = queue.Queue()
        self.stand_com = stand_com.StandCommunication("127.0.0.1",2222, self.msgQ)
        self.temp_password = None
        self.temp_dok_path = None
        self.temp_user = None
        self.commends = {"00": self.send_status, "01": self.send_status, "06": self.download, "07": self.get_doks, "11": self.all_restore_action}
        pub.subscribe(self.sign_in, "sign_in")
        pub.subscribe(self.log_in, "log_in")
        pub.subscribe(self.add_dok, "add_dok")
        pub.subscribe(self.mide_restore, "get_user_doks")
        pub.subscribe(self.restore, "restore_request")
        threading.Thread(target=self.handle_msg, daemon=True).start()

    def handle_msg(self):
        """Processes incoming messages from the queue and executes corresponding commands"""
        while True:
            packed_msg = self.msgQ.get()
            opcode, msg = stand_protocol.unpack(packed_msg)
            self.commends[opcode](msg)

    def sign_in(self, user_name, password, mail):
        """Sends a sign-in request with user details to the server"""
        self.stand_com.send_msg(stand_protocol.pack_sigh_in(opcode="00", user_name=user_name, password=password, mail=mail))

    def log_in(self, user_name, password):
        """Sends a login request with credentials to the server"""
        self.stand_com.send_msg(stand_protocol.pack_log_in(opcode= "01", user_name=user_name, password=password))

    def add_dok(self, user_name, password, dok_name, dok_path):
        """Initiates the process of adding a new DOK and stores temporary session data"""
        self.stand_com.send_msg(stand_protocol.pack_add_dok(opcode="06", user_name=user_name, dok_path=dok_name))
        self.temp_password = password
        self.temp_user = user_name
        self.temp_dok_path = dok_path

    def restore(self, user_name, dok_name, dok_path):
        """Sends a data restoration request for a specific DOK"""
        self.stand_com.send_msg(stand_protocol.pack_restore(opcode="04", user_name=user_name, dok_path=dok_name))
        self.temp_dok_path = dok_path
        self.temp_user = user_name

    def mide_restore(self, user_name):
        """Requests the list of available DOKs for the specified user"""
        self.stand_com.send_msg(stand_protocol.pack_mide_restore(opcode="07", user_name=user_name))

    def kill_temp(self):
        """Clears all temporary session variables to reset the state"""
        self.temp_password = None
        self.temp_user = None
        self.temp_dok_path = None

    def restore_to_dok(self):
        """Copies restored files from the temporary download folder to the target DOK device"""
        #כאן צריך לשנות את הנתב של הDOWNLOAD לפי המחשב שאתה נמצא עליו
        user_folder_path = os.path.join(r"C:\Users\talmid\Downloads", self.temp_user)
        if not os.path.exists(user_folder_path):
            print(f"Error: {user_folder_path} does not exist!")
            return "01"
        try:
            content = os.listdir(user_folder_path)
            if not content:
                print("User folder is empty!")
                return "01"
            dok_folder_name = content[0]
            full_dok_path = os.path.join(user_folder_path, dok_folder_name)
            print(f"Copying files from {dok_folder_name} directly to {self.temp_dok_path}...")
            for item in os.listdir(full_dok_path):
                source = os.path.join(full_dok_path, item)
                destination = os.path.join(self.temp_dok_path, item)
                if os.path.isdir(source):
                    if os.path.exists(destination):
                        shutil.rmtree(destination)
                    shutil.copytree(source, destination)
                else:
                    shutil.copy2(source, destination)
            shutil.rmtree(user_folder_path)
            print("Restore finished. Downloads folder is clean.")
            return "00"
        except Exception as e:
            print(f"An error occurred: {e}")
            return "01"

    def send_status(self, msg):
        """Prints the message status and updates the UI design queue"""
        print(msg[0])
        self.designQ.put(msg[0])

    def download(self, msg):
        """Handles the download status and triggers the executable creation process"""
        status = msg[0]
        if status == "00":
            status = create_exe.run_full_process(self.temp_dok_path, self.temp_user, self.temp_password, msg[1])
        self.kill_temp()
        self.designQ.put(status)

    def get_doks(self, msg):
        """Processes the retrieved DOK list and updates the UI queue"""
        data = msg[0]
        if not data or data == "EMPTY":
            self.designQ.put("EMPTY_RESTORE")
        else:
            formatted_msg = f"LIST:{data}"
            self.designQ.put(formatted_msg)

    def all_restore_action(self, msg):
        """Executes the full restoration sequence and manages final cleanup"""
        status = msg[0]
        if status == "00":
            status = self.restore_to_dok()
        print(f"temp's - {self.temp_user}, {self.temp_dok_path}")
        self.kill_temp()
        self.designQ.put(status)

    def get_msg(self, msg):
        """Prints the raw message content to the console"""
        print(msg)

if __name__ == '__main__':
    stand_logic = StandLogic()
    AppStand(stand_logic.designQ)