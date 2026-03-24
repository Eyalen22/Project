import wx

class MainAppPanel(wx.Panel):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.SetBackgroundColour("#1A1A1A")
        wx.StaticText(self, label="DOK EXPLORER ONLINE", pos=(100, 200)).SetForegroundColour("#00FF00")