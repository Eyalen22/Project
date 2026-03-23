import os
import sys
import threading
import shutil  # ספרייה להעתקת קבצים
import wx
from actions import cypher_files
from pubsub import pub
from design.Eject import LockProgressFrame
import logging


class DOKExplorerFrame(wx.Frame):
    def __init__(self, username, password, drive_path):
        super().__init__(None, title=f"DOK Explorer - {username}", size=(900, 600))
        self.drive_path = drive_path
        self.current_path = drive_path
        # יצירת המפתח פעם אחת בלבד
        self.key = cypher_files.create_key(username, password)
        wx.CallAfter(pub.sendMessage, "get_key", user_name=username, password=password)
        # פענוח ראשוני בעת הכניסה
        self.scan_and_process(mode="decrypt")
        self.SetBackgroundColour(wx.Colour(15, 15, 20))
        self.setup_ui()
        self.load_directory()
        self.Show()
        self.logger = logging.getLogger("logs.log")

    def setup_ui(self):
        self.panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Header setup
        header = wx.Panel(self.panel)
        header.SetBackgroundColour(wx.Colour(30, 30, 40))
        h_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.back_btn = wx.Button(header, label="BACK")

        # כפתור ADD חדש - שים לב שהוא מתווסף ל-UI
        self.add_btn = wx.Button(header, label="ADD FILE")
        self.add_btn.SetBackgroundColour(wx.Colour(40, 160, 80))  # צבע ירקרק
        self.add_btn.SetForegroundColour(wx.Colour(255, 255, 255))

        self.path_label = wx.StaticText(header, label=self.current_path)
        self.path_label.SetForegroundColour(wx.Colour(255, 255, 255))

        self.lock_btn = wx.Button(header, label="LOCK & EJECT")
        self.lock_btn.SetBackgroundColour(wx.Colour(220, 50, 50))
        self.lock_btn.SetForegroundColour(wx.Colour(255, 255, 255))

        h_sizer.Add(self.back_btn, 0, wx.ALL, 10)
        h_sizer.Add(self.add_btn, 0, wx.ALL, 10)  # הוספה לסייזר של ה-Header
        h_sizer.Add(self.path_label, 1, wx.CENTER)
        h_sizer.Add(self.lock_btn, 0, wx.ALL, 10)
        header.SetSizer(h_sizer)

        self.scrolled_window = wx.ScrolledWindow(self.panel)
        self.scrolled_window.SetScrollRate(0, 20)
        self.scrolled_window.Bind(wx.EVT_RIGHT_DOWN, self.on_right_click)
        self.list_sizer = wx.BoxSizer(wx.VERTICAL)
        self.scrolled_window.SetSizer(self.list_sizer)

        main_sizer.Add(header, 0, wx.EXPAND)
        main_sizer.Add(self.scrolled_window, 1, wx.EXPAND | wx.ALL, 5)
        self.panel.SetSizer(main_sizer)

        # קישור כפתורים לפונקציות
        self.back_btn.Bind(wx.EVT_BUTTON, self.go_back)
        self.add_btn.Bind(wx.EVT_BUTTON, self.on_add_file)  # פונקציית ההוספה
        self.lock_btn.Bind(wx.EVT_BUTTON, self.on_lock_and_exit)

    def on_add_file(self, event):
        """הוספת קבצים בצורה נקייה ואלגנטית"""
        style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE
        with wx.FileDialog(self, "בחר קבצים", wildcard="All files (*.*)|*.*", style=style) as dlg:
            if dlg.ShowModal() != wx.ID_OK:
                return
            for src in dlg.GetPaths():
                dest = os.path.join(self.current_path, os.path.basename(src))
                try:
                    shutil.copy2(src, dest)
                    cypher_files.encrypt_file(dest, self.key)
                    wx.CallAfter(pub.sendMessage, "save", file_path=dest)
                except Exception as e:
                    self.logger.error(f"Error copying {src}: {e}")

            self.load_directory()

    def scan_and_process(self, mode="encrypt"):
        """המתודה המקורית שלך לעיבוד קבצים"""
        try:
            current_executable = os.path.basename(sys.executable if getattr(sys, 'frozen', False) else __file__)
            excluded_files = {current_executable, "client_logic.exe", "logs.log"}
            excluded_dirs = {".auth_vault"}
            for root, dirs, files in os.walk(self.drive_path, topdown=True):
                dirs[:] = [d for d in dirs if d not in excluded_dirs and not d.startswith('.')]
                for file in files:
                    if file.startswith('.') or file in excluded_files:
                        continue
                    full_path = os.path.join(root, file)
                    try:
                        if os.path.isfile(full_path):
                            if mode == "decrypt":
                                cypher_files.decrypt_file_name(full_path, self.key)
                            else:
                                cypher_files.encrypt_file_name(full_path, self.key)
                    except Exception as file_error:
                        print(f"Error processing {full_path}: {file_error}")
        except Exception as e:
            print(f"General error during scan: {e}")

    def on_lock_and_exit(self, event):
        """פונקציה המופעלת בלחיצה על כפתור הנעילה"""
        self.progress_win = LockProgressFrame(self)
        self.progress_win.Show()
        self.Hide()  # הסתרת הסייר

        # הרצת תהליך הסגירה ב-Thread נפרד
        threading.Thread(target=self.run_exit_process).start()

    def run_exit_process(self):
        """מתודה המנהלת את רצף הפעולות ביציאה"""
        # 1. הצפנה מחדש (משתמש במתודה הקיימת ב-Class)
        self.scan_and_process(mode="encrypt")
        wx.CallAfter(self.progress_win.set_finished)

    def load_directory(self):
        self.list_sizer.Clear(True)
        self.path_label.SetLabel(self.current_path)
        try:
            current_exe = os.path.basename(sys.executable if getattr(sys, 'frozen', False) else __file__)
            # מיון הקבצים (תיקיות קודם ואז קבצים) נותן מראה מקצועי יותר
            items = sorted(os.listdir(self.current_path))
            for item in items:
                if item.startswith('.') or item == ".auth_vault" or item == current_exe:
                    continue
                full_path = os.path.join(self.current_path, item)
                is_dir = os.path.isdir(full_path)
                btn = wx.Button(self.scrolled_window, label=f"{'📁' if is_dir else '📄'} {item}", style=wx.BU_LEFT)
                btn.Bind(wx.EVT_LEFT_DCLICK, lambda e, p=full_path: self.handle_click(p))
                btn.Bind(wx.EVT_RIGHT_DOWN, self.on_right_click)
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
            self.logger.debug(f"you clicked on the file {path}")
            wx.CallAfter(pub.sendMessage, "new_filename", file_path=path)

    def go_back(self, e):
        parent = os.path.dirname(self.current_path)
        if len(parent) >= len(self.drive_path):
            self.current_path = parent
            self.load_directory()

    # לעשות את זה יפה
    def on_right_click(self, event):
        """תפריט הקשר חכם - מזהה אם נלחץ קובץ או שטח ריק"""
        clicked_obj = event.GetEventObject()
        menu = wx.Menu()

        # אפשרות קבועה: יצירת תיקיה
        new_folder_item = menu.Append(wx.ID_ANY, "📁 תיקיה חדשה")
        self.Bind(wx.EVT_MENU, self.on_create_folder, new_folder_item)

        # אם לחצת על כפתור (קובץ/תיקיה), נוסיף אפשרות מחיקה
        if isinstance(clicked_obj, wx.Button) and clicked_obj != self.add_btn:
            menu.AppendSeparator()
            delete_item = menu.Append(wx.ID_ANY, "🗑️ מחק")

            # שליחת הנתיב של הקובץ לפונקציית המחיקה
            # אנחנו שומרים את הנתיב בתוך ה'לייבל' או שפשוט נחלץ אותו מהטקסט
            file_name = clicked_obj.GetLabel().split(' ', 1)[-1]
            full_path = os.path.join(self.current_path, file_name)

            self.Bind(wx.EVT_MENU, lambda e: self.on_delete_item(full_path), delete_item)

        self.PopupMenu(menu)
        menu.Destroy()

    def on_create_folder(self, event):
        """דיאלוג להזנת שם התיקיה ויצירתה"""
        with wx.TextEntryDialog(self, "הזן שם לתיקיה החדשה:", "יצירת תיקיה") as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                folder_name = dlg.GetValue().strip()
                if folder_name:
                    new_folder_path = os.path.join(self.current_path, folder_name)
                    try:
                        if not os.path.exists(new_folder_path):
                            os.makedirs(new_folder_path)
                            self.logger.info(f"Created folder: {new_folder_path}")

                            # ריענון אוטומטי של התצוגה
                            self.load_directory()
                        else:
                            wx.MessageBox("תיקיה בשם זה כבר קיימת", "שגיאה", wx.OK | wx.ICON_ERROR)
                    except Exception as e:
                        self.logger.error(f"Error creating folder: {e}")
                        wx.MessageBox(f"שגיאה ביצירת התיקיה: {e}", "שגיאה", wx.OK | wx.ICON_ERROR)

    def on_delete_item(self, path):
        """מחיקת קובץ או תיקיה מה-DOK"""
        # דיאלוג אישור לפני מחיקה (חשוב בסייר קבצים!)
        item_name = os.path.basename(path)
        dial = wx.MessageDialog(self, f"האם אתה בטוח שברצונך למחוק את '{item_name}'?",
                                "אישור מחיקה", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING)

        if dial.ShowModal() == wx.ID_YES:
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)  # מחיקת תיקיה על כל תכולתה
                else:
                    os.remove(path)  # מחיקת קובץ בודד

                self.logger.info(f"Deleted: {path}")
                self.load_directory()  # ריענון התצוגה
            except Exception as e:
                wx.MessageBox(f"שגיאה במחיקה: {e}", "שגיאה", wx.OK | wx.ICON_ERROR)