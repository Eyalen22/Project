import os
import wx
import psutil
import subprocess

BG_DARK = wx.Colour(15, 15, 20)
BG_PANEL = wx.Colour(30, 30, 40)
ACCENT_CYAN = wx.Colour(0, 255, 200)
TEXT_WHITE = wx.Colour(255, 255, 255)


class DOKExplorerFrame(wx.Frame):
    def __init__(self, username):
        super().__init__(None, title=f"DOK Explorer - {username}", size=(900, 600))
        self.SetBackgroundColour(BG_DARK)

        # מציאת ה-DOK הראשון המחובר (אם קיים)
        drives = self.get_usb_drives()
        self.current_path = drives[0] if drives else ""

        self.setup_ui(drives)
        self.load_directory()
        self.Show()

    def get_usb_drives(self):
        """פונקציה שמוצאת רק כוננים נשלפים (DOK)"""
        usb_drives = []
        for partition in psutil.disk_partitions():
            if 'removable' in partition.opts or partition.fstype == "":
                # בדרך כלל כונני USB מזוהים כ-removable
                usb_drives.append(partition.mountpoint)
        return usb_drives

    def setup_ui(self, drives):
        self.panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Header
        header = wx.Panel(self.panel)
        header.SetBackgroundColour(BG_PANEL)
        h_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.back_btn = wx.Button(header, label="BACK", size=(70, 35))
        self.back_btn.SetBackgroundColour(ACCENT_CYAN)

        self.drive_selector = wx.ComboBox(header, style=wx.CB_READONLY, choices=drives)
        if drives: self.drive_selector.SetSelection(0)

        self.path_label = wx.StaticText(header, label=self.current_path)
        self.path_label.SetForegroundColour(TEXT_WHITE)

        h_sizer.Add(self.back_btn, 0, wx.ALL, 10)
        h_sizer.Add(self.drive_selector, 0, wx.CENTER | wx.RIGHT, 10)
        h_sizer.Add(self.path_label, 1, wx.CENTER)
        header.SetSizer(h_sizer)

        # רשימת קבצים
        self.scrolled_window = wx.ScrolledWindow(self.panel, style=wx.VSCROLL)
        self.scrolled_window.SetScrollRate(0, 20)
        self.list_sizer = wx.BoxSizer(wx.VERTICAL)
        self.scrolled_window.SetSizer(self.list_sizer)

        main_sizer.Add(header, 0, wx.EXPAND)
        main_sizer.Add(self.scrolled_window, 1, wx.EXPAND | wx.ALL, 5)
        self.panel.SetSizer(main_sizer)

        # Bindings
        self.back_btn.Bind(wx.EVT_BUTTON, self.go_back)
        self.drive_selector.Bind(wx.EVT_COMBOBOX, self.on_drive_change)

    def load_directory(self):
        self.list_sizer.Clear(True)
        if not self.current_path:
            msg = wx.StaticText(self.scrolled_window, label="No USB Drive Detected")
            msg.SetForegroundColour(wx.RED)
            self.list_sizer.Add(msg, 0, wx.CENTER | wx.TOP, 20)
        else:
            self.path_label.SetLabel(self.current_path)
            try:
                items = os.listdir(self.current_path)
                for item in sorted(items):
                    full_path = os.path.join(self.current_path, item)
                    is_dir = os.path.isdir(full_path)
                    btn = wx.Button(self.scrolled_window, label=f"{'📁' if is_dir else '📄'} {item}",
                                    style=wx.BU_LEFT | wx.BORDER_NONE)
                    btn.SetForegroundColour(TEXT_WHITE)
                    btn.SetBackgroundColour(BG_PANEL if is_dir else BG_DARK)
                    btn.Bind(wx.EVT_BUTTON, lambda e, p=full_path: self.handle_click(p))
                    self.list_sizer.Add(btn, 0, wx.EXPAND | wx.BOTTOM, 1)
            except Exception as e:
                print(f"Error: {e}")

        self.list_sizer.Layout()
        self.scrolled_window.FitInside()

    def handle_click(self, path):
        if os.path.isdir(path):
            self.current_path = path
            self.load_directory()
        else:
            os.startfile(path) if os.name == 'nt' else subprocess.call(['xdg-open', path])

    def on_drive_change(self, e):
        self.current_path = self.drive_selector.GetValue()
        self.load_directory()

    def go_back(self, e):
        parent = os.path.dirname(self.current_path)
        # מוודא שלא יוצאים מהכונן החוצה לסייר הכללי
        if len(parent) >= len(self.drive_selector.GetValue()):
            self.current_path = parent
            self.load_directory()