import wx
import os
import hashlib
import psutil


class LoginFrame(wx.Frame):
    def __init__(self, success_callback):
        super().__init__(None, title="Access Portal", size=(400, 500),
                         style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))

        self.success_callback = success_callback
        self.panel = wx.Panel(self)
        self.panel.SetBackgroundColour(wx.Colour(15, 15, 20))  # BG_DARK
        self.setup_ui()
        self.Show()

    def setup_ui(self):
        sizer = wx.BoxSizer(wx.VERTICAL)

        # כותרת
        title = wx.StaticText(self.panel, label="VIRTUAL DRIVE")
        title.SetForegroundColour(wx.Colour(0, 255, 200))  # ACCENT_CYAN
        title.SetFont(wx.Font(22, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))

        self.user_input = wx.TextCtrl(self.panel, size=(280, 40))
        self.user_input.SetHint("Username")

        self.pass_input = wx.TextCtrl(self.panel, size=(280, 40), style=wx.TE_PASSWORD)
        self.pass_input.SetHint("Password")

        login_btn = wx.Button(self.panel, label="AUTHENTICATE DOK", size=(280, 45))
        login_btn.SetBackgroundColour(wx.Colour(0, 255, 200))

        sizer.AddSpacer(60)
        sizer.Add(title, 0, wx.CENTER | wx.BOTTOM, 60)
        sizer.Add(self.user_input, 0, wx.CENTER | wx.BOTTOM, 15)
        sizer.Add(self.pass_input, 0, wx.CENTER | wx.BOTTOM, 20)
        sizer.Add(login_btn, 0, wx.CENTER)

        self.panel.SetSizer(sizer)
        self.Center()
        login_btn.Bind(wx.EVT_BUTTON, self.on_login)

    def find_auth_file(self):
        """מחפש את קובץ האימות בכל כונן נשלף מחובר"""
        for partition in psutil.disk_partitions():
            if 'removable' in partition.opts or partition.fstype == "":
                auth_path = os.path.join(partition.mountpoint, ".auth_vault")
                if os.path.exists(auth_path):
                    return auth_path
        return None

    def on_login(self, event):
        u_raw = self.user_input.GetValue()
        p_raw = self.pass_input.GetValue()

        auth_file = self.find_auth_file()

        if not auth_file:
            wx.MessageBox("שגיאה: ה-DOK המורשה לא נמצא במחשב.", "Access Denied", wx.ICON_ERROR)
            return

        u_hash = hashlib.sha256(u_raw.encode()).hexdigest()
        p_hash = hashlib.sha256(p_raw.encode()).hexdigest()

        try:
            with open(auth_file, "r") as f:
                lines = f.read().splitlines()
                if len(lines) >= 2:
                    if u_hash == lines[0] and p_hash == lines[1]:
                        # הצלחה!
                        self.success_callback(u_raw)
                        self.Destroy()
                        return

            wx.MessageBox("שם משתמש או סיסמה לא תואמים לכונן זה.", "Auth Failed")
        except Exception as e:
            wx.MessageBox(f"שגיאה בקריאת הכונן: {str(e)}")