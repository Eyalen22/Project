import wx
import queue

from design.panels.welcome import WelcomePanel
from design.panels.login import LoginPanel
from design.panels.register import RegisterPanel
from design.panels.main_app import MainAppPanel

class MainFrame(wx.Frame):
    def __init__(self, msg_queue):
        # Professional style: No resizing for a fixed UI look
        super().__init__(None, title="Secure DOK", size=(400, 600),
                         style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))

        self.msg_queue = msg_queue
        self.container = wx.Panel(self)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Initialize all screens
        self.screens = {
            "welcome": WelcomePanel(self.container, self),
            "login": LoginPanel(self.container, self),
            "register": RegisterPanel(self.container, self),
            "main_app": MainAppPanel(self.container, self)
        }

        # Add all to sizer but hide them initially
        for screen in self.screens.values():
            self.main_sizer.Add(screen, 1, wx.EXPAND)
            screen.Hide()

        self.container.SetSizer(self.main_sizer)
        self.show_screen("welcome")

        # Queue monitoring timer
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_check_queue, self.timer)
        self.timer.Start(100)

        self.Centre()

    def show_screen(self, name):
        """Switch between panels by name"""
        for n, p in self.screens.items():
            p.Show(n == name)
        self.container.Layout()

    def on_check_queue(self, event):
        try:
            msg = self.msg_queue.get_nowait()
            if msg == "AUTH_SUCCESS":
                self.show_screen("main_app")
        except queue.Empty:
            pass