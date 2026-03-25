import wx
from design.settings import *
from pubsub import pub
class LoginPanel(wx.Panel):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.SetBackgroundColour(BG_COLOR)

        sizer = wx.BoxSizer(wx.VERTICAL)

        header = wx.StaticText(self, label="Login to System")
        header.SetForegroundColour(TEXT_COLOR)
        header.SetFont(wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))

        self.user = wx.TextCtrl(self, size=(220, 35))
        self.user.SetHint("Username")
        self.pwd = wx.TextCtrl(self, size=(220, 35), style=wx.TE_PASSWORD)
        self.pwd.SetHint("Password")

        btn_submit = wx.Button(self, label="SIGN IN", size=(220, 40))
        btn_submit.SetBackgroundColour("#4CAF50")
        btn_submit.SetForegroundColour(TEXT_COLOR)
        btn_submit.Bind(wx.EVT_BUTTON, self.on_submit)

        btn_back = wx.Button(self, label="Back", size=(100, 30))
        btn_back.Bind(wx.EVT_BUTTON, lambda e: self.controller.show_screen("welcome"))

        sizer.AddStretchSpacer()
        sizer.Add(header, 0, wx.ALIGN_CENTER | wx.BOTTOM, 20)
        sizer.Add(self.user, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        sizer.Add(self.pwd, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        sizer.Add(btn_submit, 0, wx.ALIGN_CENTER | wx.TOP, 15)
        sizer.Add(btn_back, 0, wx.ALIGN_CENTER | wx.TOP, 10)
        sizer.AddStretchSpacer()

        self.SetSizer(sizer)

    def on_submit(self, event):
        user_name = self.user.GetValue().strip()
        password = self.pwd.GetValue().strip()

        if user_name and password:
            wx.CallAfter(pub.sendMessage, "log_in", user_name= user_name, password= password)
        else:
            wx.MessageBox("missing Credentials", "missing")
