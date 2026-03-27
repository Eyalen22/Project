import wx
from design.settings import *
from pubsub import pub

class RestorePanel(wx.Panel):
    def __init__(self, parent, controller):
        """Initializes the restore panel with a list of available backups and selection controls"""
        super().__init__(parent)
        self.controller = controller
        self.SetBackgroundColour(BG_COLOR)

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        # כותרת - בעיצוב בולט (Cyan/Accent)
        header = wx.StaticText(self, label="RESTORE YOUR DOK")
        header.SetForegroundColour(ACCENT_COLOR)
        header.SetFont(wx.Font(22, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))

        # הוראות למשתמש
        self.instruction = wx.StaticText(self, label="Select a device to restore from the list below:")
        self.instruction.SetForegroundColour(TEXT_COLOR)
        self.instruction.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_LIGHT))

        # רשימת ה-DOKs - עיצוב הייטק כהה עם טקסט ירוק
        self.dok_list = wx.ListBox(self, size=(350, 250), style=wx.LB_SINGLE | wx.BORDER_SIMPLE)
        self.dok_list.SetBackgroundColour("#1E1E1E")
        self.dok_list.SetForegroundColour("#00FF00")  # ירוק "מטריקס"
        self.dok_list.SetFont(wx.Font(12, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))

        # כפתור שחזור - יופעל רק אחרי בחירה
        self.btn_restore = wx.Button(self, label="START RESTORE", size=(220, 45))
        self.btn_restore.SetBackgroundColour(ACCENT_COLOR)
        self.btn_restore.SetForegroundColour(TEXT_COLOR)
        self.btn_restore.Bind(wx.EVT_BUTTON, self.on_restore_click)
        self.btn_restore.Disable()

        # כפתור חזור לתפריט הראשי
        btn_back = wx.Button(self, label="BACK TO MENU", size=(150, 35))
        btn_back.Bind(wx.EVT_BUTTON, lambda e: self.controller.show_screen("main_app"))

        # סידור האלמנטים במסך
        self.sizer.AddStretchSpacer()
        self.sizer.Add(header, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)
        self.sizer.Add(self.instruction, 0, wx.ALIGN_CENTER | wx.BOTTOM, 20)
        self.sizer.Add(self.dok_list, 0, wx.ALIGN_CENTER | wx.BOTTOM, 25)
        self.sizer.Add(self.btn_restore, 0, wx.ALIGN_CENTER | wx.BOTTOM, 15)
        self.sizer.Add(btn_back, 0, wx.ALIGN_CENTER)
        self.sizer.AddStretchSpacer()

        self.SetSizer(self.sizer)

        # אירוע שקורה כשלוחצים על פריט ברשימה
        self.dok_list.Bind(wx.EVT_LISTBOX, self.on_select)

    def on_select(self, event):
        """Enables the restore button once a specific backup has been selected from the list"""
        self.btn_restore.Enable()

    def update_dok_list(self, names_list):
        """Populates the listbox with backup names and updates UI instructions based on findings"""
        self.dok_list.Clear()
        if names_list:
            self.dok_list.SetItems(names_list)
            self.instruction.SetLabel(f"Found {len(names_list)} registered devices:")
            self.instruction.SetForegroundColour(TEXT_COLOR)
        else:
            self.instruction.SetLabel("No devices found for this account.")
            self.instruction.SetForegroundColour("#FF6347")  # צבע אדום-כתום לאזהרה

        self.btn_restore.Disable()  # כיבוי הכפתור כי הרשימה השתנתה
        self.Layout()

    def on_restore_click(self, event):
        """Stores the selection and transitions to the USB detection screen to begin restoration"""
        selected_dok = self.dok_list.GetStringSelection()
        if selected_dok:
            self.controller.screens["process_status_restore"].start_restore_scan(selected_dok)
            self.controller.show_screen("process_status_restore")