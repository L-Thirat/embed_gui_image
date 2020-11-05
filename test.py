#! /usr/bin/env python
#  -*- coding: utf-8 -*-
#
# GUI module generated by PAGE version 5.4
#  in conjunction with Tcl version 8.6
#    Jul 23, 2020 10:12:27 AM JST  platform: Windows NT

import sys

try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk

try:
    import ttk
    py3 = False
except ImportError:
    import tkinter.ttk as ttk
    py3 = True

# import test_support

def vp_start_gui():
    '''Starting point when module is the main routine.'''
    global val, w, root
    root = tk.Tk()
    top = Toplevel1 (root)
    # test_support.init(root, top)
    root.mainloop()

w = None
def create_Toplevel1(rt, *args, **kwargs):
    '''Starting point when module is imported by another module.
       Correct form of call: 'create_Toplevel1(root, *args, **kwargs)' .'''
    global w, w_win, root
    #rt = root
    root = rt
    w = tk.Toplevel (root)
    top = Toplevel1 (w)
    # test_support.init(w, top, *args, **kwargs)
    return (w, top)

def destroy_Toplevel1():
    global w
    w.destroy()
    w = None

class Toplevel1:
    def __init__(self, top=None):
        '''This class configures and populates the toplevel window.
           top is the toplevel containing window.'''
        _bgcolor = '#d9d9d9'  # X11 color: 'gray85'
        _fgcolor = '#000000'  # X11 color: 'black'
        _compcolor = '#d9d9d9' # X11 color: 'gray85'
        _ana1color = '#d9d9d9' # X11 color: 'gray85'
        _ana2color = '#ececec' # Closest X11 color: 'gray92'
        self.style = ttk.Style()
        if sys.platform == "win32":
            self.style.theme_use('winnative')
        self.style.configure('.',background=_bgcolor)
        self.style.configure('.',foreground=_fgcolor)
        self.style.configure('.',font="TkDefaultFont")
        self.style.map('.',background=
            [('selected', _compcolor), ('active',_ana2color)])

        top.geometry("1191x750+1762+153")
        top.minsize(120, 1)
        top.maxsize(3290, 1061)
        top.resizable(1, 1)
        top.title("New Toplevel")
        top.configure(background="#d9d9d9")

        self.Canvas1 = tk.Canvas(top)
        self.Canvas1.place(relx=0.017, rely=0.013, relheight=0.421
                , relwidth=0.296)
        self.Canvas1.configure(background="#d9d9d9")
        self.Canvas1.configure(borderwidth="2")
        self.Canvas1.configure(insertbackground="black")
        self.Canvas1.configure(relief="ridge")
        self.Canvas1.configure(selectbackground="blue")
        self.Canvas1.configure(selectforeground="white")

        self.Canvas2 = tk.Canvas(top)
        self.Canvas2.place(relx=0.344, rely=0.013, relheight=0.42
                , relwidth=0.296)
        self.Canvas2.configure(background="#d9d9d9")
        self.Canvas2.configure(borderwidth="2")
        self.Canvas2.configure(insertbackground="black")
        self.Canvas2.configure(relief="ridge")
        self.Canvas2.configure(selectbackground="blue")
        self.Canvas2.configure(selectforeground="white")

        self.Canvas3 = tk.Canvas(top)
        self.Canvas3.place(relx=0.672, rely=0.013, relheight=0.417
                , relwidth=0.313)
        self.Canvas3.configure(background="#d9d9d9")
        self.Canvas3.configure(borderwidth="2")
        self.Canvas3.configure(insertbackground="black")
        self.Canvas3.configure(relief="ridge")
        self.Canvas3.configure(selectbackground="blue")
        self.Canvas3.configure(selectforeground="white")

        self.TButton1 = ttk.Button(top)
        self.TButton1.place(relx=0.411, rely=0.52, height=55, width=206)
        self.TButton1.configure(takefocus="")
        self.TButton1.configure(text='''Tbutton''')

        self.TButton2 = ttk.Button(top)
        self.TButton2.place(relx=0.411, rely=0.627, height=55, width=206)
        self.TButton2.configure(takefocus="")
        self.TButton2.configure(text='''Tbutton''')

if __name__ == '__main__':
    vp_start_gui()




