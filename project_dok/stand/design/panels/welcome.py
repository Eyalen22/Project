import wx
from design.settings import *

class WelcomePanel(wx.Panel):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.SetBackgroundColour(BG_COLOR)

        sizer = wx.BoxSizer(wx.VERTICAL)
        title = wx.StaticText(self, label="SECURE DOK")
        title.SetForegroundColour(ACCENT_COLOR)
        title.SetFont(wx.Font(26, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))

        btn_login = wx.Button(self, label="LOGIN", size=(220, 45))
        btn_reg = wx.Button(self, label="CREATE ACCOUNT", size=(220, 45))

        btn_login.Bind(wx.EVT_BUTTON, lambda e: self.controller.show_screen("login"))
        btn_reg.Bind(wx.EVT_BUTTON, lambda e: self.controller.show_screen("register"))

        sizer.AddStretchSpacer()
        sizer.Add(title, 0, wx.ALIGN_CENTER | wx.ALL, 20)
        sizer.Add(btn_login, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        sizer.Add(btn_reg, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        sizer.AddStretchSpacer()
        self.SetSizer(sizer)