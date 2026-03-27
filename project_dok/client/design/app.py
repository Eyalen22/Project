import wx
from design.login import LoginFrame
from design.dok_explorer import DOKExplorerFrame

class App:
    """The main application controller that handles the transition from login to the secure file explorer"""
    def start_app(self):
        """Initializes the wxPython application and launches the login interface"""
        app = wx.App()
        # The success_callback ensures that the Explorer opens only after successful authentication
        LoginFrame(success_callback=lambda u, p, path: DOKExplorerFrame(u, p, path))
        app.MainLoop()

if __name__ == '__main__':
    app = App()
    app.start_app()