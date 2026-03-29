import wx


class SettingsDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title="DOK Settings", size=(450, 400))
        self.SetBackgroundColour(wx.Colour(30, 30, 40))
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        title = wx.StaticText(self, label="DOK EXPLORER GUIDE")
        title.SetForegroundColour(wx.Colour(255, 255, 255))
        font = title.GetFont()
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        title.SetFont(font)
        main_sizer.Add(title, 0, wx.ALL | wx.CENTER, 20)
        self.scrolled_window = wx.ScrolledWindow(self, style=wx.VSCROLL)
        self.scrolled_window.SetScrollRate(0, 10)
        scroll_sizer = wx.BoxSizer(wx.VERTICAL)
        instructions = (
            "1. Click 'BACKUP ALL' to sync files with the server.\n\n"
            "2. Right-click everywhere to create folders.\n\n"
            "3. Right-click on file from dell file.\n\n"
            "4. Use 'BACK' in the header to navigate up.\n\n"
            "5. The only way to add file is by pressing add inside of the dok explorer.\n\n"
            "6. Always use 'LOCK & EJECT' before removing the drive else you will kill your DOK.\n\n"
            "have a good one hope you will like the protection we provide :)"
        )

        self.content = wx.StaticText(self.scrolled_window, label=instructions)
        self.content.SetForegroundColour(wx.Colour(200, 200, 200))
        self.content.Wrap(380)  # דואג שהטקסט לא יברח מהצדדים
        scroll_sizer.Add(self.content, 1, wx.ALL | wx.EXPAND, 10)
        self.scrolled_window.SetSizer(scroll_sizer)
        main_sizer.Add(self.scrolled_window, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 15)
        self.back_to_dok = wx.Button(self, label="BACK TO DOK")
        self.back_to_dok.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(wx.ID_OK))
        main_sizer.Add(self.back_to_dok, 0, wx.ALL | wx.CENTER, 15)
        self.SetSizer(main_sizer)