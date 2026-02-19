import wx
from design.login import LoginFrame
from design.dok_explorer import DOKExplorerFrame

class App:
    def start_app(self):
        app = wx.App()
        LoginFrame(success_callback=lambda u, p, path: DOKExplorerFrame(u, p, path))
        app.MainLoop()

if __name__ == '__main__':
    app = App()
    app.start_app()