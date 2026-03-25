import wx
from design.settings import *

class ProcessStatusPanel(wx.Panel):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.SetBackgroundColour(BG_COLOR)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.status_title = wx.StaticText(self, label="")
        self.status_title.SetFont(wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        self.detail_text = wx.StaticText(self, label="", style=wx.ALIGN_CENTER)
        self.detail_text.SetForegroundColour(TEXT_COLOR)
        self.detail_text.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_LIGHT))
        self.btn_back = wx.Button(self, label="back to the Menu", size=(200, 50))
        self.btn_back.Bind(wx.EVT_BUTTON, lambda e: self.controller.show_screen("main_app"))
        self.btn_back.Hide()

        self.sizer.AddStretchSpacer()
        self.sizer.Add(self.status_title, 0, wx.ALIGN_CENTER | wx.BOTTOM, 20)
        self.sizer.Add(self.detail_text, 0, wx.ALIGN_CENTER | wx.BOTTOM, 40)
        self.sizer.Add(self.btn_back, 0, wx.ALIGN_CENTER)
        self.sizer.AddStretchSpacer()

        self.SetSizer(self.sizer)

    def show_waiting(self):
        self.status_title.SetLabel("WAIT FOR DOWNLOADING YOUR FILES")
        self.status_title.SetForegroundColour("#FFD700") # צהוב
        self.detail_text.SetLabel("אנא אל תנתק את ה-DOK מהמחשב ברגע זה...")
        self.btn_back.Hide()
        self.Layout()

    def set_final_status(self, success=True):
        if success:
            self.status_title.SetLabel("download was a Success")
            self.status_title.SetForegroundColour("#00FF00") # ירוק
            self.detail_text.SetLabel("Success! The system files have been installed on your DOK.\nYou may now safely remove it from the computer.")
        else:
            self.status_title.SetLabel("download was'n a Success")
            self.status_title.SetForegroundColour("#FF0000") # אדום
            self.detail_text.SetLabel("There was an error downloading the system files to your DOK.\nPlease try again or contact the system administrator.")

        self.btn_back.Show()
        self.Layout()