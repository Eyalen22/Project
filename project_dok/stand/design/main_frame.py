import wx
import queue

# ייבוא הפאנלים
from design.panels.welcome import WelcomePanel
from design.panels.login import LoginPanel
from design.panels.register import RegisterPanel
from design.panels.main.main_app import MainAppPanel
from design.panels.main.add.add_dok import AddDokPanel
from design.panels.main.restore.restore import RestorePanel
from design.panels.main.add.confirm_add import ConfirmAddPanel
from design.panels.main.add.process_status import ProcessStatusPanel # ייבוא המסך החדש

class MainFrame(wx.Frame):
    def __init__(self, msg_queue):
        super().__init__(None, title="Secure DOK System", size=(800, 600))

        self.msg_queue = msg_queue

        # --- הכספת הסודית בזיכרון (RAM) ---
        self.temp_user = None
        self.temp_pass = None
        self.container = wx.Panel(self)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.screens = {
            "welcome": WelcomePanel(self.container, self),
            "login": LoginPanel(self.container, self),
            "register": RegisterPanel(self.container, self),
            "main_app": MainAppPanel(self.container, self),
            "add_dok": AddDokPanel(self.container, self),
            "restore_dok": RestorePanel(self.container, self),
            "confirm_add": ConfirmAddPanel(self.container, self),
            "process_status": ProcessStatusPanel(self.container, self)
        }

        for screen in self.screens.values():
            self.main_sizer.Add(screen, 1, wx.EXPAND)
            screen.Hide()

        self.container.SetSizer(self.main_sizer)
        self.show_screen("welcome")
        # self.Maximize(True)

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_check_queue, self.timer)
        self.timer.Start(100)

    def show_screen(self, name):
        """מעבר בין מסכים + ניקוי שדות בחזרה לתפריט"""
        if name == "welcome":
            self.clear_auth_fields()
        for n, p in self.screens.items():
            p.Show(n == name)
        if name == "add_dok":
            self.screens["add_dok"].start_scan()
        self.container.Layout()

    def logout_user(self):
        """פונקציית ניקוי רעלים - מוחקת הכל מהזיכרון"""
        self.temp_user = None
        self.temp_pass = None
        self.show_screen("welcome")

    def on_check_queue(self, event):
        try:
            msg = self.msg_queue.get_nowait()
            is_in_process_screen = self.screens["process_status"].IsShown()
            if msg == "00":
                if is_in_process_screen:
                    self.screens["process_status"].set_final_status(success=True)
                else:
                    self.handle_auth_success()
            elif msg == "01":
                if is_in_process_screen:
                    self.screens["process_status"].set_final_status(success=False)
                else:
                    wx.MessageBox("Invalid Credentials", "error", wx.OK | wx.ICON_ERROR)

        except queue.Empty:
            pass

    def handle_auth_success(self):
        """לוגיקה לשמירת פרטים ומעבר למסך הראשי אחרי לוגין מוצלח"""
        active = "login" if self.screens["login"].IsShown() else "register"
        self.temp_user = self.screens[active].user.GetValue()
        self.temp_pass = self.screens[active].pwd.GetValue()
        self.screens["login"].user.Clear()
        self.screens["login"].pwd.Clear()
        self.screens["register"].user.Clear()
        self.screens["register"].pwd.Clear()
        self.screens["register"].email.Clear()
        self.screens["main_app"].update_user(self.temp_user)
        self.show_screen("main_app")

    def clear_auth_fields(self):
        """מנקה את כל שדות הטקסט של ההתחברות וההרשמה"""
        self.screens["login"].user.Clear()
        self.screens["login"].pwd.Clear()
        self.screens["register"].user.Clear()
        self.screens["register"].pwd.Clear()
        self.screens["register"].email.Clear() # הוספנו גם את המייל
