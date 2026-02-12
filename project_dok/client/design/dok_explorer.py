import os
import sys

import wx
import psutil
import subprocess

BG_DARK = wx.Colour(15, 15, 20)
BG_PANEL = wx.Colour(30, 30, 40)
ACCENT_CYAN = wx.Colour(0, 255, 200)
TEXT_WHITE = wx.Colour(255, 255, 255)


class DOKExplorerFrame(wx.Frame):
    def __init__(self, username, drive_path):  # הוספת drive_path כפרמטר
        super().__init__(None, title=f"DOK Explorer - {username}", size=(900, 600))
        self.SetBackgroundColour(BG_DARK)

        self.authorized_drive = drive_path
        self.current_path = drive_path

        self.setup_ui()
        self.load_directory()
        self.Show()

    def setup_ui(self):
        self.panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        header = wx.Panel(self.panel)
        header.SetBackgroundColour(BG_PANEL)
        h_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.back_btn = wx.Button(header, label="BACK", size=(70, 35))
        self.back_btn.SetBackgroundColour(ACCENT_CYAN)

        # הורדנו את ה-ComboBox כי אנחנו נעולים על כונן אחד
        self.path_label = wx.StaticText(header, label=self.current_path)
        self.path_label.SetForegroundColour(TEXT_WHITE)

        h_sizer.Add(self.back_btn, 0, wx.ALL, 10)
        h_sizer.Add(self.path_label, 1, wx.CENTER)
        header.SetSizer(h_sizer)

        self.scrolled_window = wx.ScrolledWindow(self.panel, style=wx.VSCROLL)
        self.scrolled_window.SetScrollRate(0, 20)
        self.list_sizer = wx.BoxSizer(wx.VERTICAL)
        self.scrolled_window.SetSizer(self.list_sizer)

        main_sizer.Add(header, 0, wx.EXPAND)
        main_sizer.Add(self.scrolled_window, 1, wx.EXPAND | wx.ALL, 5)
        self.panel.SetSizer(main_sizer)

        self.back_btn.Bind(wx.EVT_BUTTON, self.go_back)

    def handle_click(self, path):
        if os.path.isdir(path):
            self.current_path = path
            self.load_directory()
        else:
            try:
                # פתיחת הקובץ באמצעות אפליקציית ברירת המחדל של המערכת
                if os.name == 'nt':  # Windows
                    os.startfile(path)
                else:  # Linux / Mac
                    subprocess.call(['open' if sys.platform == 'darwin' else 'xdg-open', path])
            except Exception as e:
                wx.MessageBox(f"לא ניתן לפתוח את הקובץ: {str(e)}", "שגיאה", wx.ICON_ERROR)

    def is_hidden(self, filepath):
        """בודק אם קובץ מוסתר או קובץ מערכת"""
        name = os.path.basename(filepath)
        # מסתיר קבצים שמתחילים בנקודה או את קובץ ה-vault עצמו
        if name.startswith('.') or name == ".auth_vault":
            return True

        if os.name == 'nt':
            try:
                import ctypes
                attrs = ctypes.windll.kernel32.GetFileAttributesW(filepath)
                # 2 זה מוסתר, 4 זה קובץ מערכת
                return attrs != -1 and (attrs & 2 or attrs & 4)
            except:
                return False
        return False

    def load_directory(self):
        self.list_sizer.Clear(True)
        self.path_label.SetLabel(self.current_path)

        try:
            items = os.listdir(self.current_path)
            for item in sorted(items):
                full_path = os.path.join(self.current_path, item)

                # סינון קבצים מוסתרים
                if self.is_hidden(full_path):
                    continue

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

    def go_back(self, e):
        parent = os.path.dirname(self.current_path)
        # מוודא שלא יוצאים מחוץ לכונן המורשה
        if len(parent) >= len(self.authorized_drive):
            self.current_path = parent
            self.load_directory()