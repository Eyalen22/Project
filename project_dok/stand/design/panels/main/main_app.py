import wx
from design.settings import *
from pubsub import pub  # אל תשכח לייבא את pub

class MainAppPanel(wx.Panel):
    def __init__(self, parent, controller):
        """Initializes the main command center panel with navigation buttons and session information"""
        super().__init__(parent)
        self.controller = controller
        self.SetBackgroundColour(BG_COLOR)

        self.username = ""
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.header = wx.StaticText(self, label="SECURE COMMAND CENTER")
        self.header.SetForegroundColour("#00FF00")
        self.header.SetFont(wx.Font(22, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))

        self.user_welcome = wx.StaticText(self, label="Welcome, Agent")
        self.user_welcome.SetForegroundColour(TEXT_COLOR)
        self.user_welcome.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_LIGHT))

        # כפתורים
        self.btn_add = self.create_styled_button("ADD NEW DOK", "#1A1A1A", "#4CAF50")
        self.btn_restore = self.create_styled_button("RESTORE BACKUP", "#1A1A1A", "#2196F3")
        self.btn_logout = self.create_styled_button("LOG OUT", "#1A1A1A", "#F44336")

        # --- אירועים מעודכנים ---
        self.btn_add.Bind(wx.EVT_BUTTON, lambda e: self.controller.show_screen("add_dok"))

        # שינינו את זה מ-lambda לפונקציה מסודרת ששולחת PUB
        self.btn_restore.Bind(wx.EVT_BUTTON, self.on_restore_click)

        self.btn_logout.Bind(wx.EVT_BUTTON, self.on_logout)

        # סידור בתוך המסך
        main_sizer.Add(self.header, 0, wx.ALIGN_CENTER | wx.TOP, 40)
        main_sizer.Add(self.user_welcome, 0, wx.ALIGN_CENTER | wx.BOTTOM, 50)
        main_sizer.Add(self.btn_add, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        main_sizer.Add(self.btn_restore, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        main_sizer.AddStretchSpacer()
        main_sizer.Add(self.btn_logout, 0, wx.ALIGN_CENTER | wx.BOTTOM, 40)

        self.SetSizer(main_sizer)

    def on_restore_click(self, event):
        """Requests the list of available DOKs from the logic layer before transitioning to the restore screen"""
        wx.CallAfter(pub.sendMessage, "get_user_doks", user_name=self.username)
        self.btn_restore.SetLabel("LOADING LIST...")
        self.btn_restore.Disable()

    def create_styled_button(self, label, bg, border_color):
        """Creates a button with custom styling and hover effects for a consistent UI look"""
        btn = wx.Button(self, label=label, size=(280, 60))
        btn.SetBackgroundColour(bg)
        btn.SetForegroundColour(TEXT_COLOR)
        btn.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        btn.Bind(wx.EVT_ENTER_WINDOW, lambda e: btn.SetBackgroundColour(border_color))
        btn.Bind(wx.EVT_LEAVE_WINDOW, lambda e: btn.SetBackgroundColour(bg))
        return btn

    def update_user(self, username):
        """Updates the displayed username and resets the interactive state of the control buttons"""
        self.username = username
        self.user_welcome.SetLabel(f"Active Session: {username.upper()}")
        self.btn_restore.SetLabel("RESTORE BACKUP")  # מחזיר את הטקסט המקורי
        self.btn_restore.Enable()  # מחזיר אותו להיות לחיץ
        self.Layout()  # מרענן את התצוגה של הפאנל

    def on_logout(self, event):
        """Triggers the logout process through the controller to clear the current session"""
        self.controller.logout_user()