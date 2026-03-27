import wx
from pubsub import pub
from design.settings import *

class ConfirmAddPanel(wx.Panel):
    def __init__(self, parent, controller):
        """Initializes the confirmation panel for confirming the selected USB device before processing"""
        super().__init__(parent)
        self.controller = controller
        self.SetBackgroundColour(BG_COLOR)

        self.drive_name = ""
        self.drive_letter = ""

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.title = wx.StaticText(self, label="DOK CONFIRMATION")
        self.title.SetForegroundColour("#00FF00")
        self.title.SetFont(wx.Font(22, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))

        self.name_label = wx.StaticText(self, label="Device: [Pending]")
        self.name_label.SetForegroundColour(TEXT_COLOR)
        self.name_label.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_LIGHT))

        self.btn_guide = self.create_styled_button("USER GUIDE", "#2196F3")
        self.btn_guide.Bind(wx.EVT_BUTTON, self.on_guide)

        self.btn_start = self.create_styled_button("START ADDING DOK", "#4CAF50")
        self.btn_start.Bind(wx.EVT_BUTTON, self.on_start)

        self.btn_cancel = wx.Button(self, label="CANCEL", size=(100, 30))
        self.btn_cancel.Bind(wx.EVT_BUTTON, lambda e: self.controller.show_screen("main_app"))

        sizer.Add(self.title, 0, wx.ALIGN_CENTER | wx.TOP, 60)
        sizer.Add(self.name_label, 0, wx.ALIGN_CENTER | wx.TOP, 20)
        sizer.AddStretchSpacer(1)
        sizer.Add(self.btn_guide, 0, wx.ALIGN_CENTER | wx.ALL, 15)
        sizer.Add(self.btn_start, 0, wx.ALIGN_CENTER | wx.ALL, 15)
        sizer.AddStretchSpacer(1)
        sizer.Add(self.btn_cancel, 0, wx.ALIGN_CENTER | wx.BOTTOM, 40)

        self.SetSizer(sizer)

    def create_styled_button(self, label, color):
        """Creates a consistent styled button for the confirmation interface"""
        btn = wx.Button(self, label=label, size=(300, 60))
        btn.SetBackgroundColour(color)
        btn.SetForegroundColour(TEXT_COLOR)
        btn.SetFont(wx.Font(13, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        return btn

    def setup_drive(self, name, letter):
        """Updates the device details on the panel before the screen is displayed to the user"""
        self.drive_name = name
        self.drive_letter = letter
        self.name_label.SetLabel(f"Detected: {name} ({letter})")
        self.Layout()

    def on_guide(self, event):
        """Displays a guide message box with instructions for safely adding a new DOK"""
        guide_msg = (
            "1. Ensure the DOK remains connected throughout the process.\n"
            "2. Do not close the application until the success message appears.\n"
            "3. the dok has to be fresh and new else it won't work good for you."
        )
        wx.MessageBox(guide_msg, "User Guide", wx.OK | wx.ICON_INFORMATION)

    def on_start(self, event):
        """Transitions to the process status screen and publishes an event to start the DOK addition logic"""
        # הכנת מסך הסטטוס למצב המתנה
        self.controller.screens["process_status_add"].show_waiting()
        self.controller.show_screen("process_status_add")

        # שליחת הודעת ה-PubSub ללוגיקה
        wx.CallAfter(pub.sendMessage, "add_dok",
                     user_name=self.controller.temp_user,
                     password=self.controller.temp_pass,
                     dok_name=self.drive_name,
                     dok_path=self.drive_letter)