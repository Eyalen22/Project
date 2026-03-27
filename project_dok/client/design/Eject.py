import os
import wx

class LockProgressFrame(wx.Frame):
    """A progress window displayed during the final drive encryption process to prevent premature removal"""
    def __init__(self, parent):
        super().__init__(parent, title="Locking Drive...", size=(400, 220),
                         style=wx.CAPTION | wx.STAY_ON_TOP)
        self.SetBackgroundColour(wx.Colour(30, 30, 40))
        self.Center()
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.status_label = wx.StaticText(panel, label="Locking... Please do not eject the DOK", style=wx.ALIGN_CENTER)
        self.status_label.SetForegroundColour(wx.Colour(255, 255, 255))
        self.gauge = wx.Gauge(panel, range=100, size=(250, 25))
        self.gauge.Pulse()
        self.done_btn = wx.Button(panel, label="Finish & Exit")
        self.done_btn.SetBackgroundColour(wx.Colour(50, 150, 50))
        self.done_btn.Hide()
        self.done_btn.Bind(wx.EVT_BUTTON, self.on_exit_click)
        sizer.AddStretchSpacer()
        sizer.Add(self.status_label, 0, wx.CENTER | wx.ALL, 15)
        sizer.Add(self.gauge, 0, wx.CENTER | wx.ALL, 10)
        sizer.Add(self.done_btn, 0, wx.CENTER | wx.ALL, 10)
        sizer.AddStretchSpacer()
        panel.SetSizer(sizer)

    def set_finished(self):
        """Updates the UI to indicate that the drive is safely locked and ready for removal"""
        self.gauge.SetValue(100)
        self.status_label.SetLabel("Drive locked successfully!\nYou may now eject the DOK.")
        self.done_btn.Show()
        self.Layout()

    def on_exit_click(self, event):
        """Cleans up the application and exits the process"""
        self.Destroy()
        wx.GetApp().ExitMainLoop()
        os._exit(0)