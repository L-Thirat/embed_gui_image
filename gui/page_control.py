import tkinter as tki


class Page(tki.Frame):
    def __init__(self, *args, **kwargs):
        tki.Frame.__init__(self, *args, **kwargs)

    def show(self):
        self.lift()
