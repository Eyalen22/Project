import wx
import queue
from design.main_frame import MainFrame

class AppStand(wx.App):
    def __init__(self, msg_queue):
        self.msg_queue = msg_queue
        # Initializing the app and starting the MainLoop automatically
        super().__init__(clearSigInt=True)
        self.MainLoop()

    def OnInit(self):
        # Create and show the frame manager
        self.frame = MainFrame(self.msg_queue)
        self.frame.Show()
        return True

if __name__ == '__main__':
    # Shared communication queue
    communication_queue = queue.Queue()

    # Instantiate the app object - this starts the entire UI
    AppStand(communication_queue)