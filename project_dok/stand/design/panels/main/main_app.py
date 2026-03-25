import wx
from design.settings import *

class MainAppPanel(wx.Panel):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.SetBackgroundColour(BG_COLOR)

        self.username = ""
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.header = wx.StaticText(self, label="SECURE COMMAND CENTER")
        self.header.SetForegroundColour("#00FF00") # ירוק "מטריקס"
        self.header.SetFont(wx.Font(22, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))

        self.user_welcome = wx.StaticText(self, label="Welcome, Agent")
        self.user_welcome.SetForegroundColour(TEXT_COLOR)
        self.user_welcome.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_LIGHT))

        # כפתורים
        self.btn_add = self.create_styled_button("ADD NEW DOK", "#1A1A1A", "#4CAF50")
        self.btn_restore = self.create_styled_button("RESTORE BACKUP", "#1A1A1A", "#2196F3")
        self.btn_logout = self.create_styled_button("LOG OUT", "#1A1A1A", "#F44336")

        # אירועים - עובר אוטומטית למסכים החדשים
        self.btn_add.Bind(wx.EVT_BUTTON, lambda e: self.controller.show_screen("add_dok"))
        self.btn_restore.Bind(wx.EVT_BUTTON, lambda e: self.controller.show_screen("restore_dok"))
        self.btn_logout.Bind(wx.EVT_BUTTON, self.on_logout)

        # סידור בתוך המסך
        main_sizer.Add(self.header, 0, wx.ALIGN_CENTER | wx.TOP, 40)
        main_sizer.Add(self.user_welcome, 0, wx.ALIGN_CENTER | wx.BOTTOM, 50)

        main_sizer.Add(self.btn_add, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        main_sizer.Add(self.btn_restore, 0, wx.ALIGN_CENTER | wx.ALL, 10)

        main_sizer.AddStretchSpacer()
        main_sizer.Add(self.btn_logout, 0, wx.ALIGN_CENTER | wx.BOTTOM, 40)

        self.SetSizer(main_sizer)

    def create_styled_button(self, label, bg, border_color):
        """יוצר כפתור עם עיצוב מודרני"""
        btn = wx.Button(self, label=label, size=(280, 60))
        btn.SetBackgroundColour(bg)
        btn.SetForegroundColour(TEXT_COLOR)
        btn.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))

        # אפקט פשוט למעבר עכבר
        btn.Bind(wx.EVT_ENTER_WINDOW, lambda e: btn.SetBackgroundColour(border_color))
        btn.Bind(wx.EVT_LEAVE_WINDOW, lambda e: btn.SetBackgroundColour(bg))
        return btn

    def update_user(self, username):
        self.username = username
        self.user_welcome.SetLabel(f"Active Session: {username.upper()}")
        self.Layout()

    def on_logout(self, event):
        self.controller.logout_user()