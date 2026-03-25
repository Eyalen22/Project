from design.settings import *
import wx
class RestorePanel(wx.Panel):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.SetBackgroundColour(BG_COLOR)

        sizer = wx.BoxSizer(wx.VERTICAL)
        label = wx.StaticText(self, label="WELCOME TO RESTORE SECTION")
        label.SetForegroundColour(TEXT_COLOR)

        btn = wx.Button(self, label="BACK")
        btn.Bind(wx.EVT_BUTTON, lambda e: self.controller.show_screen("main_app"))

        sizer.Add(label, 0, wx.ALL | wx.ALIGN_CENTER, 50)
        sizer.Add(btn, 0, wx.ALIGN_CENTER)
        self.SetSizer(sizer)