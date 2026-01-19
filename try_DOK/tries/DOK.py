import os
import wx
import json
import string
import subprocess

# --- AUTHENTICATION SYSTEM ---
USER_DB = "users.json"


def load_users():
    if not os.path.exists(USER_DB): return {}
    try:
        with open(USER_DB, "r") as f:
            return json.load(f)
    except:
        return {}


def save_user(username, password):
    users = load_users()
    users[username] = password
    with open(USER_DB, "w") as f: json.dump(users, f)


# --- STYLING ---
BG_DARK = wx.Colour(15, 15, 20)
BG_PANEL = wx.Colour(30, 30, 40)
ACCENT_CYAN = wx.Colour(0, 255, 200)
TEXT_WHITE = wx.Colour(255, 255, 255)


class LoginFrame(wx.Frame):
    def __init__(self, success_callback):
        super().__init__(None, title="Access Portal", size=(400, 500),
                         style=wx.DEFAULT_FRAME_STYLE & ~(wx.RESIZE_BORDER | wx.MAXIMIZE_BOX))
        self.success_callback = success_callback
        self.panel = wx.Panel(self)
        self.panel.SetBackgroundColour(BG_DARK)

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Title
        self.title = wx.StaticText(self.panel, label="VIRTUAL DRIVE")
        self.title.SetForegroundColour(ACCENT_CYAN)
        self.title.SetFont(wx.Font(22, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))

        # --- Initial Buttons Container ---
        self.btn_container = wx.BoxSizer(wx.VERTICAL)

        self.start_login_btn = wx.Button(self.panel, label="LOGIN", size=(250, 60))
        self.start_signup_btn = wx.Button(self.panel, label="SIGN UP", size=(250, 60))

        for b in [self.start_login_btn, self.start_signup_btn]:
            b.SetBackgroundColour(BG_PANEL)
            b.SetForegroundColour(ACCENT_CYAN)
            b.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))

        self.btn_container.Add(self.start_login_btn, 0, wx.CENTER | wx.BOTTOM, 20)
        self.btn_container.Add(self.start_signup_btn, 0, wx.CENTER, 20)

        # --- Hidden Input Container ---
        self.input_container = wx.BoxSizer(wx.VERTICAL)

        self.user_input = wx.TextCtrl(self.panel, size=(280, 40))
        self.user_input.SetHint("Username")
        self.pass_input = wx.TextCtrl(self.panel, size=(280, 40), style=wx.TE_PASSWORD)
        self.pass_input.SetHint("Password")

        self.confirm_btn = wx.Button(self.panel, label="CONFIRM", size=(280, 45))
        self.confirm_btn.SetBackgroundColour(ACCENT_CYAN)
        self.back_to_menu = wx.StaticText(self.panel, label="← Back to Menu")
        self.back_to_menu.SetForegroundColour(wx.LIGHT_GREY)

        self.input_container.Add(self.user_input, 0, wx.CENTER | wx.BOTTOM, 15)
        self.input_container.Add(self.pass_input, 0, wx.CENTER | wx.BOTTOM, 20)
        self.input_container.Add(self.confirm_btn, 0, wx.CENTER | wx.BOTTOM, 10)
        self.input_container.Add(self.back_to_menu, 0, wx.CENTER)

        # Hide inputs initially
        self.input_container.ShowItems(False)

        # Main Layout
        self.main_sizer.AddSpacer(60)
        self.main_sizer.Add(self.title, 0, wx.CENTER | wx.BOTTOM, 60)
        self.main_sizer.Add(self.btn_container, 0, wx.CENTER)
        self.main_sizer.Add(self.input_container, 0, wx.CENTER)

        self.panel.SetSizer(self.main_sizer)
        self.Center()

        # Bindings
        self.start_login_btn.Bind(wx.EVT_BUTTON, lambda e: self.show_inputs("login"))
        self.start_signup_btn.Bind(wx.EVT_BUTTON, lambda e: self.show_inputs("signup"))
        self.confirm_btn.Bind(wx.EVT_BUTTON, self.on_confirm)
        self.back_to_menu.Bind(wx.EVT_LEFT_DOWN, self.show_menu)

        self.mode = ""  # track if we are logging in or signing up
        self.Show()

    def show_inputs(self, mode):
        self.mode = mode
        self.btn_container.ShowItems(False)
        self.input_container.ShowItems(True)
        self.confirm_btn.SetLabel("PROCEED LOGIN" if mode == "login" else "CREATE ACCOUNT")
        self.panel.Layout()

    def show_menu(self, event):
        self.input_container.ShowItems(False)
        self.btn_container.ShowItems(True)
        self.panel.Layout()

    def on_confirm(self, event):
        users = load_users()
        u, p = self.user_input.GetValue(), self.pass_input.GetValue()
        if not u or not p:
            wx.MessageBox("Fields cannot be empty")
            return

        if self.mode == "login":
            if u in users and users[u] == p:
                self.success_callback(u)
                self.Destroy()
            else:
                wx.MessageBox("Invalid Credentials")
        else:
            save_user(u, p)
            wx.MessageBox(f"Success! Now please Login.")
            self.show_menu(None)


class FileExplorerFrame(wx.Frame):
    def __init__(self, username):
        super().__init__(None, title=f"Explorer - {username}", size=(1000, 700))
        self.SetBackgroundColour(BG_DARK)
        self.current_path = os.path.abspath("C:\\")

        self.panel = wx.Panel(self)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Header
        header = wx.Panel(self.panel)
        header.SetBackgroundColour(BG_PANEL)
        h_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.back_btn = wx.Button(header, label="BACK", size=(70, 35))
        self.back_btn.SetBackgroundColour(ACCENT_CYAN)
        self.drive_selector = wx.ComboBox(header, style=wx.CB_READONLY, size=(80, -1))
        self.path_label = wx.StaticText(header, label=self.current_path)
        self.path_label.SetForegroundColour(TEXT_WHITE)

        h_sizer.Add(self.back_btn, 0, wx.ALL, 10)
        h_sizer.Add(self.drive_selector, 0, wx.CENTER | wx.RIGHT, 10)
        h_sizer.Add(self.path_label, 1, wx.CENTER)
        header.SetSizer(h_sizer)

        # Explorer List
        self.scrolled_window = wx.ScrolledWindow(self.panel, style=wx.VSCROLL)
        self.scrolled_window.SetScrollRate(0, 20)
        self.list_sizer = wx.BoxSizer(wx.VERTICAL)
        self.scrolled_window.SetSizer(self.list_sizer)

        self.main_sizer.Add(header, 0, wx.EXPAND)
        self.main_sizer.Add(self.scrolled_window, 1, wx.EXPAND | wx.ALL, 5)
        self.panel.SetSizer(self.main_sizer)

        self.update_drive_list()
        self.load_directory()

        self.back_btn.Bind(wx.EVT_BUTTON, self.go_back)
        self.drive_selector.Bind(wx.EVT_COMBOBOX, self.on_drive_change)
        self.Show()

    def update_drive_list(self):
        drives = [f"{l}:\\" for l in string.ascii_uppercase if os.path.exists(f"{l}:\\")]
        self.drive_selector.SetItems(drives)
        self.drive_selector.SetValue("C:\\")

    def load_directory(self):
        self.list_sizer.Clear(True)
        self.path_label.SetLabel(self.current_path)
        try:
            items = os.listdir(self.current_path)
            items.sort(key=lambda x: os.path.isdir(os.path.join(self.current_path, x)), reverse=True)
            for item in items:
                full_path = os.path.join(self.current_path, item)
                is_dir = os.path.isdir(full_path)
                btn = wx.Button(self.scrolled_window, label=f"{'📁' if is_dir else '📄'} {item}",
                                style=wx.BU_LEFT | wx.BORDER_NONE)
                btn.SetForegroundColour(TEXT_WHITE)
                btn.SetBackgroundColour(BG_PANEL if is_dir else BG_DARK)
                btn.Bind(wx.EVT_BUTTON, lambda evt, p=full_path: self.handle_click(p))
                self.list_sizer.Add(btn, 0, wx.EXPAND | wx.BOTTOM, 1)
        except:
            pass
        self.list_sizer.Layout()
        self.scrolled_window.FitInside()

    def handle_click(self, path):
        if os.path.isdir(path):
            self.current_path = path
            self.load_directory()
        else:
            try:
                os.startfile(path) if os.name == 'nt' else subprocess.call(['xdg-open', path])
            except:
                pass

    def on_drive_change(self, e):
        self.current_path = self.drive_selector.GetValue()
        self.load_directory()

    def go_back(self, e):
        parent = os.path.dirname(self.current_path)
        if parent != self.current_path:
            self.current_path = parent
            self.load_directory()


if __name__ == "__main__":
    app = wx.App()
    LoginFrame(success_callback=lambda u: FileExplorerFrame(u))
    app.MainLoop()