import os
import sys
import threading
import shutil
import wx
from actions import cypher_files
from pubsub import pub
from design.Eject import LockProgressFrame
import logging

class DOKExplorerFrame(wx.Frame):
    """A custom file explorer that automatically manages encryption/decryption of drive content"""
    def __init__(self, username, password, drive_path):
        """Initializes the secure explorer, processes initial decryption, and sets up the user interface"""
        super().__init__(None, title=f"DOK Explorer - {username}", size=(900, 600))
        self.drive_path = drive_path
        self.current_path = drive_path
        self.key = cypher_files.create_key(username, password)
        wx.CallAfter(pub.sendMessage, "get_key", user_name=username, password=password)
        self.scan_and_process(mode="decrypt")
        self.SetBackgroundColour(wx.Colour(15, 15, 20))
        self.setup_ui()
        self.load_directory()
        self.Show()
        self.logger = logging.getLogger("logs.log")

    def setup_ui(self):
        """Builds the graphical interface including the file list view and the control header"""
        self.panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        header = wx.Panel(self.panel)
        header.SetBackgroundColour(wx.Colour(30, 30, 40))
        h_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.back_btn = wx.Button(header, label="BACK")
        self.add_btn = wx.Button(header, label="ADD FILE")
        self.add_btn.SetBackgroundColour(wx.Colour(40, 160, 80))
        self.path_label = wx.StaticText(header, label=self.current_path)
        self.path_label.SetForegroundColour(wx.Colour(255, 255, 255))
        self.lock_btn = wx.Button(header, label="LOCK & EJECT")
        self.lock_btn.SetBackgroundColour(wx.Colour(220, 50, 50))

        h_sizer.Add(self.back_btn, 0, wx.ALL, 10)
        h_sizer.Add(self.add_btn, 0, wx.ALL, 10)
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
        self.add_btn.Bind(wx.EVT_BUTTON, self.on_add_file)
        self.lock_btn.Bind(wx.EVT_BUTTON, self.on_lock_and_exit)

    def on_add_file(self, event):
        """Imports external files to the drive and automatically encrypts them upon addition"""
        style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE
        with wx.FileDialog(self, "Select Files", wildcard="All files (*.*)|*.*", style=style) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
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
        """Recursively scans the drive to encrypt or decrypt files based on the specified mode"""
        try:
            current_executable = os.path.basename(sys.executable if getattr(sys, 'frozen', False) else __file__)
            excluded_files = {current_executable, "client_logic.exe", "logs.log"}
            excluded_dirs = {".auth_vault"}
            for root, dirs, files in os.walk(self.drive_path, topdown=True):
                dirs[:] = [d for d in dirs if d not in excluded_dirs and not d.startswith('.')]
                for file in files:
                    if file.startswith('.') or file in excluded_files: continue
                    full_path = os.path.join(root, file)
                    if os.path.isfile(full_path):
                        if mode == "decrypt": cypher_files.decrypt_file_name(full_path, self.key)
                        else: cypher_files.encrypt_file_name(full_path, self.key)
        except Exception as e: print(f"General error during scan: {e}")

    def on_lock_and_exit(self, event):
        """Transitions to the lock screen and starts the background re-encryption process"""
        self.progress_win = LockProgressFrame(self)
        self.progress_win.Show()
        self.Hide()
        threading.Thread(target=self.run_exit_process).start()

    def run_exit_process(self):
        """Performs final drive locking (encryption) before application exit"""
        self.scan_and_process(mode="encrypt")
        wx.CallAfter(self.progress_win.set_finished)

    def load_directory(self):
        """Populates the list view with items from the current directory path"""
        self.list_sizer.Clear(True)
        self.path_label.SetLabel(self.current_path)
        try:
            current_exe = os.path.basename(sys.executable if getattr(sys, 'frozen', False) else __file__)
            items = sorted(os.listdir(self.current_path))
            for item in items:
                if item.startswith('.') or item == ".auth_vault" or item == current_exe: continue
                full_path = os.path.join(self.current_path, item)
                is_dir = os.path.isdir(full_path)
                btn = wx.Button(self.scrolled_window, label=f"{'📁' if is_dir else '📄'} {item}", style=wx.BU_LEFT)
                btn.Bind(wx.EVT_LEFT_DCLICK, lambda e, p=full_path: self.handle_click(p))
                btn.Bind(wx.EVT_RIGHT_DOWN, self.on_right_click)
                self.list_sizer.Add(btn, 0, wx.EXPAND | wx.BOTTOM, 1)
        except: pass
        self.list_sizer.Layout()
        self.scrolled_window.FitInside()

    def handle_click(self, path):
        """Navigates into folders or opens a file monitor for secure file access"""
        if os.path.isdir(path):
            self.current_path = path
            self.load_directory()
        else:
            wx.CallAfter(pub.sendMessage, "new_filename", file_path=path)

    def go_back(self, e):
        """Navigates to the parent directory while ensuring the user doesn't exit the DOK root"""
        parent = os.path.dirname(self.current_path)
        if len(parent) >= len(self.drive_path):
            self.current_path = parent
            self.load_directory()

    def on_right_click(self, event):
        """Displays a context menu for folder creation or item deletion"""
        clicked_obj = event.GetEventObject()
        menu = wx.Menu()
        new_folder_item = menu.Append(wx.ID_ANY, "📁 תיקיה חדשה")
        self.Bind(wx.EVT_MENU, self.on_create_folder, new_folder_item)
        if isinstance(clicked_obj, wx.Button) and clicked_obj != self.add_btn:
            menu.AppendSeparator()
            delete_item = menu.Append(wx.ID_ANY, "🗑️ מחק")
            file_name = clicked_obj.GetLabel().split(' ', 1)[-1]
            full_path = os.path.join(self.current_path, file_name)
            self.Bind(wx.EVT_MENU, lambda e: self.on_delete_item(full_path), delete_item)
        self.PopupMenu(menu)
        menu.Destroy()

    def on_create_folder(self, event):
        """Prompts for a folder name and creates a new directory on the drive"""
        with wx.TextEntryDialog(self, "Enter folder name:", "New Folder") as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                folder_name = dlg.GetValue().strip()
                if folder_name:
                    new_path = os.path.join(self.current_path, folder_name)
                    if not os.path.exists(new_path):
                        os.makedirs(new_path)
                        self.load_directory()

    def on_delete_item(self, path):
        """Confirms and executes the deletion of a file or folder from the drive"""
        dial = wx.MessageDialog(self, f"Delete '{os.path.basename(path)}'?", "Confirm Delete", wx.YES_NO | wx.ICON_WARNING)
        if dial.ShowModal() == wx.ID_YES:
            try:
                if os.path.isdir(path): shutil.rmtree(path)
                else: os.remove(path)
                self.load_directory()
            except Exception: pass