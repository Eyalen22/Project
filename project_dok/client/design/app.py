import wx
from login import LoginFrame
from dok_explorer import DOKExplorerFrame


def start_app():
    app = wx.App()
    # ה-Callback פותח את הסייר רק אחרי התחברות מוצלחת
    LoginFrame(success_callback=lambda user: DOKExplorerFrame(user))
    app.MainLoop()

if __name__ == "__main__":
    start_app()