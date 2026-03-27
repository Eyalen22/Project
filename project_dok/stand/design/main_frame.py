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
from design.panels.main.add.process_status_add import ProcessStatusPanelAdd
from design.panels.main.restore.process_status_restore import ProcessStatusPanelRestore

class MainFrame(wx.Frame):
    def __init__(self, msg_queue):
        """Initializes the main window, container panel, and all application screens"""
        super().__init__(None, title="Secure DOK System", size=(800, 600))

        self.msg_queue = msg_queue

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
            "process_status_add": ProcessStatusPanelAdd(self.container, self),
            "process_status_restore": ProcessStatusPanelRestore(self.container, self)
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
        """Switches between different panels and clears authentication fields when returning to the welcome screen"""
        if name == "welcome":
            self.clear_auth_fields()
        for n, p in self.screens.items():
            p.Show(n == name)
        if name == "add_dok":
            self.screens["add_dok"].start_scan()
        elif name == "main_app":
            self.screens["main_app"].update_user(self.temp_user)
            for n, p in self.screens.items():
                p.Show(n == name)
        self.container.Layout()

    def logout_user(self):
        """Clears user credentials from memory and redirects to the welcome screen"""
        self.temp_user = None
        self.temp_pass = None
        self.show_screen("welcome")

    def on_check_queue(self, event):
        """Periodically checks the message queue for server responses and updates the UI state accordingly"""
        try:
            msg = self.msg_queue.get_nowait()
            is_in_add_process = self.screens["process_status_add"].IsShown()
            is_in_restore_process = self.screens["process_status_restore"].IsShown()
            if isinstance(msg, str) and msg.startswith("LIST:"):
                actual_data = msg.replace("LIST:", "")
                raw_list = actual_data.split("@#")
                clean_list = [name.strip() for name in raw_list if name.strip()]
                self.screens["restore_dok"].update_dok_list(clean_list)
                self.show_screen("restore_dok")
            elif msg == "EMPTY_RESTORE":
                self.screens["restore_dok"].update_dok_list([])
                self.show_screen("restore_dok")
            elif msg == "00":
                if is_in_add_process:
                    self.screens["process_status_add"].set_final_status(success=True)
                elif is_in_restore_process:
                    self.screens["process_status_restore"].set_final_status(success=True)
                else:
                    self.handle_auth_success()
            elif msg == "01":
                if is_in_add_process:
                    self.screens["process_status_add"].set_final_status(success=False)
                elif is_in_restore_process:
                    self.screens["process_status_restore"].set_final_status(success=False)
                else:
                    wx.MessageBox("Action failed. Check your credentials.", "Error", wx.OK | wx.ICON_ERROR)
        except queue.Empty:
            pass

    def handle_auth_success(self):
        """Saves user information and transitions to the main application panel after successful authentication"""
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
        """Clears all text input fields in the login and registration panels"""
        self.screens["login"].user.Clear()
        self.screens["login"].pwd.Clear()
        self.screens["register"].user.Clear()
        self.screens["register"].pwd.Clear()
        self.screens["register"].email.Clear() # הוספנו גם את המייל