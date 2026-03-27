import wx
import threading
import time
import os
import string
from pubsub import pub

class ProcessStatusPanelRestore(wx.Panel):
    def __init__(self, parent, controller):
        """Initializes the restore status panel, including status labels and the background scanning components"""
        super().__init__(parent)
        self.controller = controller
        self.SetBackgroundColour("#2b2b2b")

        self.selected_backup = ""
        self.scanning = False
        self.initial_drives = []

        # שימוש ב-main_sizer לכל אורך המחלקה
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        # טקסט סטטוס ראשי
        self.status_label = wx.StaticText(self, label="PREPARING...")
        self.status_label.SetForegroundColour("#ffffff")
        self.status_label.SetFont(wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))

        # טקסט מידע משני (הודעות הצלחה/שגיאה יופיעו כאן)
        self.device_info = wx.StaticText(self, label="")
        self.device_info.SetForegroundColour("#bbbbbb")
        self.device_info.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))

        # כפתור ביטול סריקה - משתמש ב-show_screen ישירות
        self.cancel_button = wx.Button(self, label="Cancel Search", size=(200, 50))
        self.cancel_button.Bind(wx.EVT_BUTTON, lambda e: self.on_cancel_search())
        self.cancel_button.Hide()

        # בניית המבנה הממורכז
        self.main_sizer.AddStretchSpacer()
        self.main_sizer.Add(self.status_label, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        self.main_sizer.Add(self.device_info, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        self.main_sizer.Add(self.cancel_button, 0, wx.ALIGN_CENTER | wx.ALL, 20)
        self.main_sizer.AddStretchSpacer()

        self.SetSizer(self.main_sizer)

    def start_restore_scan(self, backup_name):
        """Prepares the UI and starts a background thread to detect a newly inserted USB drive for restoration"""
        self.selected_backup = backup_name
        self.scanning = True
        self.initial_drives = self.get_drive_list()

        self.status_label.SetLabel("PLEASE INSERT YOUR DOK")
        self.status_label.SetForegroundColour("#FFD700")
        self.device_info.SetLabel("Waiting for a new USB device...")

        self.cancel_button.Show()
        self.Layout()

        threading.Thread(target=self.scan_loop, daemon=True).start()

    def get_drive_list(self):
        """Retrieves a list of currently mounted drive letters on the local machine"""
        return [f"{letter}:\\" for letter in string.ascii_uppercase if os.path.exists(f"{letter}:\\")]

    def scan_loop(self):
        """Continuously monitors for new drives and triggers the restoration process upon detection"""
        while self.scanning:
            current_drives = self.get_drive_list()
            new_found = [d for d in current_drives if d not in self.initial_drives]
            if new_found:
                drive_letter = new_found[0]
                wx.CallAfter(self.on_device_detected, drive_letter)
                break
            time.sleep(1)

    def on_cancel_search(self):
        """Stops the USB monitoring process and redirects the user to the main application menu"""
        self.scanning = False
        self.controller.show_screen("main_app")

    def on_device_detected(self, drive_letter):
        """Updates the UI to reflect drive detection and sends a request to the server to begin file restoration"""
        self.scanning = False
        self.cancel_button.Hide()

        self.status_label.SetLabel("DOK DETECTED!")
        self.status_label.SetForegroundColour("#00FF00")
        self.device_info.SetLabel("Restoring files, please wait...")
        self.Layout()

        wx.CallAfter(pub.sendMessage, "restore_request",
                     user_name=self.controller.temp_user,
                     dok_name=self.selected_backup,
                     dok_path=drive_letter)

    def set_final_status(self, success):
        """Displays the final outcome of the restoration process and provides navigation back to the menu"""
        self.scanning = False

        if success:
            self.status_label.SetLabel("RESTORE SUCCESSFUL!")
            self.status_label.SetForegroundColour("#00FF00")
            self.device_info.SetLabel("הכל עבר חלק")
        else:
            self.status_label.SetLabel("RESTORE FAILED")
            self.status_label.SetForegroundColour("#FF0000")
            self.device_info.SetLabel("אין קבצים לגיבוי כאן")

        self.device_info.SetForegroundColour("#ffffff")
        self.cancel_button.Hide()
        if not hasattr(self, 'btn_back'):
            self.btn_back = wx.Button(self, label="back to the Menu", size=(200, 50))
            self.btn_back.Bind(wx.EVT_BUTTON, lambda e: self.controller.show_screen("main_app"))
            self.main_sizer.Add(self.btn_back, 0, wx.ALL | wx.ALIGN_CENTER, 20)

        self.Layout()