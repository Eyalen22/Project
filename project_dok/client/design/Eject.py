import wx
from pubsub import pub
class LockProgressFrame(wx.Frame):
    """חלון המתנה שמופיע בזמן תהליך הנעילה הסופי"""

    def __init__(self, parent):
        # השארתי את STAY_ON_TOP כדי שהמשתמש לא יפספס את הודעת הסיום
        super().__init__(parent, title="Locking Drive...", size=(400, 220),
                         style=wx.CAPTION | wx.STAY_ON_TOP)
        self.SetBackgroundColour(wx.Colour(30, 30, 40))
        self.Center()

        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # תווית סטטוס
        self.status_label = wx.StaticText(panel, label="מבצע נעילה מחדש... נא לא להוציא את ה-DOK",
                                          style=wx.ALIGN_CENTER)
        self.status_label.SetForegroundColour(wx.Colour(255, 255, 255))

        # מד התקדמות (Progress Bar)
        self.gauge = wx.Gauge(panel, range=100, size=(250, 25))
        self.gauge.Pulse()

        # כפתור היציאה - מוסתר כברירת מחדל
        self.done_btn = wx.Button(panel, label="סיום ויציאה מהמערכת")
        self.done_btn.SetBackgroundColour(wx.Colour(50, 150, 50))  # צבע ירוק לסיום
        self.done_btn.SetForegroundColour(wx.Colour(255, 255, 255))
        self.done_btn.Hide()

        # קישור הכפתור לפונקציית הסגירה
        self.done_btn.Bind(wx.EVT_BUTTON, self.on_exit_click)

        # סידור האלמנטים בחלון
        sizer.AddStretchSpacer()
        sizer.Add(self.status_label, 0, wx.CENTER | wx.ALL, 15)
        sizer.Add(self.gauge, 0, wx.CENTER | wx.ALL, 10)
        sizer.Add(self.done_btn, 0, wx.CENTER | wx.ALL, 10)
        sizer.AddStretchSpacer()

        panel.SetSizer(sizer)

    def set_finished(self):
        """נקרא מה-Thread הראשי כשפעולת ההצפנה מסתיימת"""
        self.gauge.SetValue(100)  # ממלא את הפס עד הסוף
        self.status_label.SetLabel("הכונן ננעל בהצלחה!\nאתה מוזמן להוציא את ה-DOK ולצאת.")
        self.done_btn.Show()  # מציג את הכפתור
        self.Layout()  # מרענן את סידור החלון כדי שהכפתור יופיע נכון

    def on_exit_click(self, event):
        """סוגר את החלון ואת האפליקציה כולה"""
        self.Destroy()  # סוגר את החלון הנוכחי
        wx.GetApp().ExitMainLoop()  # יוצא מהלולאה הראשית של wxPython בצורה נקייה