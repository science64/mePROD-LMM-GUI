"""
mePROD App v3.0.1 - Entry Point
Süleyman Bozkurt @2026
"""

import sys
import ctypes
from tkinter import Tk
from src.gui import MyWindow

__version__ = "v3.0.1"

if __name__ == '__main__':
    # Enable DPI awareness for sharp text on high-resolution screens
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    root = Tk()

    # Scale window and fonts according to the actual screen DPI
    dpi = root.winfo_fpixels('1i')
    scale = dpi / 96.0
    root.tk.call('tk', 'scaling', dpi / 72.0)

    root.title(f"mePROD App {__version__} by S. Bozkurt @2026")

    # Window size — scaled to match DPI, not resizable
    win_w, win_h = int(780 * scale), int(660 * scale)
    root.geometry(f"{win_w}x{win_h}")
    root.resizable(False, False)

    # Center on screen
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    x = (ws // 2) - (win_w // 2)
    y = (hs // 2) - (win_h // 2)
    root.geometry(f'+{x}+{y}')

    MyWindow(root)

    try:
        root.wm_iconbitmap('files//icon.ico')
    except Exception:
        pass

    root.mainloop()