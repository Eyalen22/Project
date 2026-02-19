import wx
import os
import sys
from actions import cypher_files  # וודא שהנתיב מוגדר ב-sys.path אם הקובץ בתיקייה אחרת
from pubsub import pub

class DOKExplorerFrame(wx.Frame):
    def __init__(self, username, password, drive_path):
        super().__init__(None, title=f"DOK Explorer - {username}", size=(900, 600))
        self.drive_path = drive_path
        self.current_path = drive_path
        self.key = cypher_files.create_key(username, password)
        self.scan_and_process(mode="decrypt")
        self.SetBackgroundColour(wx.Colour(15, 15, 20))
        self.setup_ui()
        self.load_directory()
        self.Show()

    def setup_ui(self):
        self.panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        header = wx.Panel(self.panel)
        header.SetBackgroundColour(wx.Colour(30, 30, 40))
        h_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.back_btn = wx.Button(header, label="BACK")
        self.path_label = wx.StaticText(header, label=self.current_path)
        self.path_label.SetForegroundColour(wx.Colour(255, 255, 255))

        self.lock_btn = wx.Button(header, label="LOCK & EJECT")
        self.lock_btn.SetBackgroundColour(wx.Colour(220, 50, 50))
        self.lock_btn.SetForegroundColour(wx.Colour(255, 255, 255))

        h_sizer.Add(self.back_btn, 0, wx.ALL, 10)
        h_sizer.Add(self.path_label, 1, wx.CENTER)
        h_sizer.Add(self.lock_btn, 0, wx.ALL, 10)
        header.SetSizer(h_sizer)

        self.scrolled_window = wx.ScrolledWindow(self.panel)
        self.scrolled_window.SetScrollRate(0, 20)
        self.list_sizer = wx.BoxSizer(wx.VERTICAL)
        self.scrolled_window.SetSizer(self.list_sizer)

        main_sizer.Add(header, 0, wx.EXPAND)
        main_sizer.Add(self.scrolled_window, 1, wx.EXPAND | wx.ALL, 5)
        self.panel.SetSizer(main_sizer)

        self.back_btn.Bind(wx.EVT_BUTTON, self.go_back)
        self.lock_btn.Bind(wx.EVT_BUTTON, self.on_lock_and_exit)

    def scan_and_process(self, mode="decrypt"):
        """סורק את ה-DOK ומפעיל את הפונקציות שלך עם החרגת ה-EXE"""
        try:
            # זיהוי שם הקובץ שמריץ את התוכנה כרגע (ה-EXE או ה-Python script)
            current_executable = os.path.basename(sys.executable if getattr(sys, 'frozen', False) else __file__)

            for file in os.listdir(self.drive_path):
                # החרגות: קבצים מוסתרים, ה-Vault, וה-EXE עצמו
                if (file.startswith('.') or
                        file == ".auth_vault" or
                        file == current_executable or
                        file == "app.exe"):  # ליתר ביטחון החרגנו גם שם גנרי אם הגדרת כזה
                    continue

                full_path = os.path.join(self.drive_path, file)
                if os.path.isfile(full_path):
                    if mode == "decrypt":
                        cypher_files.decrypt_file_name(full_path, self.key)
                    else:
                        cypher_files.encrypt_file_name(full_path, self.key)
        except Exception as e:
            print(f"Error processing files: {e}")

    def on_lock_and_exit(self, event):
        self.scan_and_process(mode="encrypt")
        wx.Exit()

    # שאר המתודות (load_directory, handle_click, go_back) נשארות ללא שינוי...
    def load_directory(self):
        self.list_sizer.Clear(True)
        self.path_label.SetLabel(self.current_path)
        try:
            current_exe = os.path.basename(sys.executable if getattr(sys, 'frozen', False) else __file__)
            for item in os.listdir(self.current_path):
                if item.startswith('.') or item == ".auth_vault" or item == current_exe:
                    continue
                full_path = os.path.join(self.current_path, item)
                is_dir = os.path.isdir(full_path)
                btn = wx.Button(self.scrolled_window, label=f"{'📁' if is_dir else '📄'} {item}", style=wx.BU_LEFT)
                btn.Bind(wx.EVT_BUTTON, lambda e, p=full_path: self.handle_click(p))
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
            print("in file exp:", path)
            wx.CallAfter(pub.sendMessage,"new_filename", file_path=path)

            os.startfile(path) if os.name == 'nt' else None

    def go_back(self, e):
        parent = os.path.dirname(self.current_path)
        if len(parent) >= len(self.drive_path):
            self.current_path = parent
            self.load_directory()