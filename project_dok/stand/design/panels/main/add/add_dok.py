import wx
import threading
import time
import os
import string
import ctypes
from design.settings import *

class AddDokPanel(wx.Panel):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.SetBackgroundColour(BG_COLOR)

        self.scanning = False
        self.initial_drives = [] # רשימת הכוננים שהיו מחוברים בהתחלה

        sizer = wx.BoxSizer(wx.VERTICAL)

        # כותרת סטטוס
        self.status_label = wx.StaticText(self, label="READY TO SCAN...")
        self.status_label.SetForegroundColour("#FFD700")
        self.status_label.SetFont(wx.Font(18, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))

        # תצוגת שם הכונן שנמצא
        self.device_info = wx.StaticText(self, label="Waiting for USB insertion...")
        self.device_info.SetForegroundColour(TEXT_COLOR)
        self.device_info.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))

        self.btn_back = wx.Button(self, label="BACK TO MENU", size=(150, 40))
        self.btn_back.Bind(wx.EVT_BUTTON, self.on_back)

        sizer.AddStretchSpacer()
        sizer.Add(self.status_label, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)
        sizer.Add(self.device_info, 0, wx.ALIGN_CENTER | wx.BOTTOM, 30)
        sizer.Add(self.btn_back, 0, wx.ALIGN_CENTER)
        sizer.AddStretchSpacer()
        self.SetSizer(sizer)

    def get_drive_list(self):
        """הלוגיקה שלך: מחזירה רשימת אותיות כוננים קיימים"""
        return [f"{letter}:\\" for letter in string.ascii_uppercase if os.path.exists(f"{letter}:\\")]

    def get_volume_name(self, drive_letter):
        """שואב את השם הפנימי של ה-DOK (למשל 'EYAL_USB')"""
        try:
            kernel32 = ctypes.windll.kernel32
            volumeNameBuffer = ctypes.create_unicode_buffer(1024)
            # משתמש בנתיב הכונן כדי למצוא את השם שלו במערכת
            kernel32.GetVolumeInformationW(ctypes.c_wchar_p(drive_letter), volumeNameBuffer, 1024, None, None, None, None, 0)
            return volumeNameBuffer.value if volumeNameBuffer.value else "Unnamed Drive"
        except:
            return "Unknown Device"

    def start_scan(self):
        """פונקציה שנקראת מה-FrameManager כשנכנסים למסך"""
        if self.scanning:
            return
        self.scanning = True
        self.initial_drives = self.get_drive_list()
        self.status_label.SetLabel("MONITORING USB PORTS...")
        self.device_info.SetLabel("Please insert your DOK now")
        threading.Thread(target=self.scan_loop, daemon=True).start()

    def scan_loop(self):
        """לולאת הבדיקה השקטה"""
        while self.scanning:
            current_drives = self.get_drive_list()
            new_found = [d for d in current_drives if d not in self.initial_drives]
            if new_found:
                drive_letter = new_found[0] # למשל "F:\"
                volume_name = self.get_volume_name(drive_letter)
                wx.CallAfter(self.on_device_detected, volume_name, drive_letter)
                break
            time.sleep(1)

    def on_device_detected(self, name, letter):
        """פונקציה שנקראת מה-scan_loop כשנמצא כונן חדש"""
        self.scanning = False # עוצרים את ה-Thread של הסריקה
        self.controller.screens["confirm_add"].setup_drive(name, letter)
        wx.CallAfter(self.controller.show_screen, "confirm_add")

    def on_back(self, event):
        self.scanning = False
        self.controller.show_screen("main_app")