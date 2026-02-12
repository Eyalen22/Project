import wx
import os
import hashlib
import sys


class LoginFrame(wx.Frame):
    def __init__(self, success_callback):
        # הגדרת חלון ללא אפשרות הגדלה/הקטנה למראה מקצועי
        super().__init__(None, title="Access Portal", size=(400, 500),
                         style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))

        self.success_callback = success_callback
        self.panel = wx.Panel(self)
        self.panel.SetBackgroundColour(wx.Colour(15, 15, 20))  # BG_DARK
        self.setup_ui()
        self.Show()

    def setup_ui(self):
        sizer = wx.BoxSizer(wx.VERTICAL)

        # כותרת האפליקציה
        title = wx.StaticText(self.panel, label="VIRTUAL DRIVE")
        title.SetForegroundColour(wx.Colour(0, 255, 200))  # ACCENT_CYAN
        title.SetFont(wx.Font(22, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))

        # שדות קלט
        self.user_input = wx.TextCtrl(self.panel, size=(280, 40))
        self.user_input.SetHint("Username")

        self.pass_input = wx.TextCtrl(self.panel, size=(280, 40), style=wx.TE_PASSWORD)
        self.pass_input.SetHint("Password")

        # כפתור התחברות
        login_btn = wx.Button(self.panel, label="AUTHENTICATE DOK", size=(280, 45))
        login_btn.SetBackgroundColour(wx.Colour(0, 255, 200))
        login_btn.SetForegroundColour(wx.Colour(15, 15, 20))  # טקסט כהה על כפתור בהיר

        # סידור האלמנטים
        sizer.AddSpacer(60)
        sizer.Add(title, 0, wx.CENTER | wx.BOTTOM, 60)
        sizer.Add(self.user_input, 0, wx.CENTER | wx.BOTTOM, 15)
        sizer.Add(self.pass_input, 0, wx.CENTER | wx.BOTTOM, 20)
        sizer.Add(login_btn, 0, wx.CENTER)

        self.panel.SetSizer(sizer)
        self.Center()

        # קישור כפתור לפעולה
        login_btn.Bind(wx.EVT_BUTTON, self.on_login)

    def get_auth_file(self):
        """
        מזהה את הנתיב לקובץ ה-Vault.
        אם האפליקציה רצה כ-EXE, הקובץ נמצא בתיקייה הזמנית הפנימית (_MEIPASS).
        אם האפליקציה רצה מ-PyCharm, הוא מחפש בתיקייה של הסקריפט.
        """
        if getattr(sys, 'frozen', False):
            # נתיב פנימי של PyInstaller
            base_path = sys._MEIPASS
        else:
            # נתיב עבודה רגיל
            base_path = os.path.dirname(os.path.abspath(__file__))

        return os.path.join(base_path, ".auth_vault")

    def on_login(self, event):
        u_raw = self.user_input.GetValue()
        p_raw = self.pass_input.GetValue()
        auth_file = self.get_auth_file()

        # בדיקת דיבאג (תמחק את זה אחרי שזה יעבוד)
        if not os.path.exists(auth_file):
            wx.MessageBox(f"הקובץ לא נמצא בנתיב:\n{auth_file}", "Debug Info")
            return

        u_hash = hashlib.sha256(u_raw.encode()).hexdigest()
        p_hash = hashlib.sha256(p_raw.encode()).hexdigest()

        try:
            with open(auth_file, "r") as f:
                content = f.read().splitlines()
                if len(content) >= 2:
                    saved_u, saved_p = content[0], content[1]

                    if u_hash == saved_u and p_hash == saved_p:
                        exe_path = sys.executable if getattr(sys, 'frozen', False) else __file__
                        drive_path = os.path.splitdrive(os.path.abspath(exe_path))[0] + os.sep
                        self.success_callback(u_raw, drive_path)
                        self.Destroy()
                    else:
                        wx.MessageBox("שם משתמש או סיסמה לא נכונים.", "Auth Failed")
        except Exception as e:
            wx.MessageBox(f"שגיאה בקריאה: {str(e)}")


# חלק זה מיועד רק לבדיקה ידנית של הקובץ אם מריצים אותו ישירות
if __name__ == '__main__':
    app = wx.App()
    LoginFrame(success_callback=lambda u, p: print(f"Logged in: {u} on {p}"))
    app.MainLoop()