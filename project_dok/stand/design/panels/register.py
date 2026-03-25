import wx
from design.settings import *
from pubsub import pub

class RegisterPanel(wx.Panel):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.SetBackgroundColour(BG_COLOR)

        sizer = wx.BoxSizer(wx.VERTICAL)

        header = wx.StaticText(self, label="Create New Account")
        header.SetForegroundColour(TEXT_COLOR)
        header.SetFont(wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))

        self.user = wx.TextCtrl(self, size=(220, 35))
        self.user.SetHint("Username")

        self.email = wx.TextCtrl(self, size=(220, 35))
        self.email.SetHint("Email Address")

        self.pwd = wx.TextCtrl(self, size=(220, 35), style=wx.TE_PASSWORD)
        self.pwd.SetHint("Password")

        btn_reg = wx.Button(self, label="REGISTER NOW", size=(220, 40))
        btn_reg.SetBackgroundColour(ACCENT_COLOR)
        btn_reg.SetForegroundColour(TEXT_COLOR)
        btn_reg.Bind(wx.EVT_BUTTON, self.on_register)

        # כפתור חזור שהיה חסר
        btn_back = wx.Button(self, label="Back to Menu", size=(120, 30))
        btn_back.Bind(wx.EVT_BUTTON, lambda e: self.controller.show_screen("welcome"))

        sizer.AddStretchSpacer()
        sizer.Add(header, 0, wx.ALIGN_CENTER | wx.BOTTOM, 20)
        sizer.Add(self.user, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        sizer.Add(self.email, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        sizer.Add(self.pwd, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        sizer.Add(btn_reg, 0, wx.ALIGN_CENTER | wx.TOP, 15)
        sizer.Add(btn_back, 0, wx.ALIGN_CENTER | wx.TOP, 10)
        sizer.AddStretchSpacer()

        self.SetSizer(sizer)

    def on_register(self, event):
        user_name = self.user.GetValue().strip()
        mail = self.email.GetValue().strip()
        password = self.pwd.GetValue().strip()

        if user_name and mail and password:
            wx.CallAfter(pub.sendMessage, "sign_in", user_name=user_name, mail=mail, password=password)
        else:
            wx.MessageBox("missing Credentials", "missing")
