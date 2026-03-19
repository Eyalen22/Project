import wx
import os
import hashlib
import sys
import shutil

class LoginFrame(wx.Frame):
    def __init__(self, success_callback):
        super().__init__(None, title="DOK Access Portal", size=(400, 500),
                         style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        self.success_callback = success_callback
        self.panel = wx.Panel(self)
        self.tries = 0
        self.panel.SetBackgroundColour(wx.Colour(15, 15, 20))
        self.setup_ui()
        self.Show()

    def setup_ui(self):
        sizer = wx.BoxSizer(wx.VERTICAL)
        title = wx.StaticText(self.panel, label="VIRTUAL DRIVE")
        title.SetForegroundColour(wx.Colour(0, 255, 200))
        title.SetFont(wx.Font(22, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))

        self.user_input = wx.TextCtrl(self.panel, size=(280, 40))
        self.user_input.SetHint("Username")
        self.pass_input = wx.TextCtrl(self.panel, size=(280, 40), style=wx.TE_PASSWORD)
        self.pass_input.SetHint("Password")

        login_btn = wx.Button(self.panel, label="AUTHENTICATE", size=(280, 45))
        login_btn.SetBackgroundColour(wx.Colour(0, 255, 200))

        sizer.AddSpacer(60);
        sizer.Add(title, 0, wx.CENTER | wx.BOTTOM, 60)
        sizer.Add(self.user_input, 0, wx.CENTER | wx.BOTTOM, 15)
        sizer.Add(self.pass_input, 0, wx.CENTER | wx.BOTTOM, 20)
        sizer.Add(login_btn, 0, wx.CENTER)
        self.panel.SetSizer(sizer)
        self.Center()
        login_btn.Bind(wx.EVT_BUTTON, self.on_login)

    def on_login(self, event):
        u_raw, p_raw = self.user_input.GetValue(), self.pass_input.GetValue()
        base_path = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
        auth_file = os.path.join(base_path, ".auth_vault")

        u_hash = hashlib.sha256(u_raw.encode()).hexdigest()
        p_hash = hashlib.sha256(p_raw.encode()).hexdigest()

        try:
            with open(auth_file, "r") as f:
                content = f.read().splitlines()
                if len(content) >= 2 and u_hash == content[0] and p_hash == content[1]:
                    # מזהה את כונן ה-DOK עליו רצה האפליקציה
                    exe_path = sys.executable if getattr(sys, 'frozen', False) else __file__
                    drive_path = os.path.splitdrive(os.path.abspath(exe_path))[0] + os.sep
                    self.success_callback(u_raw, p_raw, drive_path)
                    self.Destroy()
                else:
                    wx.MessageBox("Invalid Credentials", "Auth Failed")
                    self.tries += 1
                    if self.tries == 3:
                        self.del_dok()
        except Exception as e:
            wx.MessageBox(f"File Error: {str(e)}")

    def del_dok(self):
        """מחיקת כל הקבצים בכונן וסגירת התוכנית"""
        exe_path = sys.executable if getattr(sys, 'frozen', False) else __file__
        drive_path = os.path.splitdrive(os.path.abspath(exe_path))[0] + os.sep
        current_file = os.path.abspath(exe_path)
        try:
            for filename in os.listdir(drive_path):
                file_path = os.path.join(drive_path, filename)
                full_path = os.path.abspath(file_path)
                if full_path == current_file:
                    continue
                try:
                    if os.path.isfile(full_path) or os.path.islink(full_path):
                        os.unlink(full_path)
                    elif os.path.isdir(full_path):
                        shutil.rmtree(full_path)
                except Exception as e:
                    print(f"Could not delete {filename}: {e}")
        finally:
            self.Destroy()  # סוגר את החלון הנוכחי
            wx.GetApp().ExitMainLoop()  # יוצא מהלולאה הראשית של wxPython בצורה נקייה