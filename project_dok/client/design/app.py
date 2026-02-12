import wx
import client_logic
from login import LoginFrame
from dok_explorer import DOKExplorerFrame


class App:
    def __init__(self):
        self.client_log = client_logic.clientLogic()

    def start_app(self):
        app = wx.App()
        LoginFrame(success_callback=lambda user, path: DOKExplorerFrame(user, path))
        app.MainLoop()

if __name__ == '__main__':
    app = App()
    app.start_app()



