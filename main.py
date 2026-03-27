"""
mePROD App v3.0.0 - Entry Point
Süleyman Bozkurt @2026
"""

import sys
from tkinter import Tk
from src.gui import MyWindow

__version__ = "v3.0.0"

if __name__ == '__main__':
    root = Tk()
    root.title(f"mePROD App {__version__} by S. Bozkurt @2026")

    # Window size — fixed, not resizable
    win_w, win_h = 960, 760
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