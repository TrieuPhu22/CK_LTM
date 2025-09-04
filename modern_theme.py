import tkinter as tk
from tkinter import ttk

_LIGHT = {
    "bg": "#F7F7FA",
    "fg": "#1F2937",
    "fg_muted": "#4B5563",
    "accent": "#2563EB",
    "surface": "#FFFFFF",
    "border": "#E5E7EB",
    "row_alt": "#F3F4F6",
    "select_bg": "#DBEAFE",
}
_DARK = {
    "bg": "#0F172A",
    "fg": "#E5E7EB",
    "fg_muted": "#9CA3AF",
    "accent": "#60A5FA",
    "surface": "#111827",
    "border": "#1F2937",
    "row_alt": "#0B1221",
    "select_bg": "#1D4ED8",
}

_current_mode = "light"

def apply_theme(root: tk.Tk | tk.Toplevel, mode: str = "light") -> None:
    """Áp theme cho app. mode: 'light' | 'dark'"""
    global _current_mode
    _current_mode = mode = (mode or "light").lower()
    palette = _LIGHT if mode == "light" else _DARK

    style = ttk.Style(root)

  
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    # Nền gốc
    root.configure(bg=palette["bg"])

    # ------ Các thành phần cơ bản ------
    style.configure(".", background=palette["bg"], foreground=palette["fg"])
    style.configure("TLabel", background=palette["bg"], foreground=palette["fg"])
    style.configure("TFrame", background=palette["bg"])
    style.configure("TLabelframe", background=palette["bg"], foreground=palette["fg"])
    style.configure("TLabelframe.Label", background=palette["bg"], foreground=palette["fg_muted"])

    style.configure("TButton",
                    background=palette["surface"], foreground=palette["fg"],
                    padding=6, borderwidth=1, relief="raised")
    style.map("TButton",
              background=[("active", palette["select_bg"])],
              relief=[("pressed", "sunken")])

    style.configure("TEntry",
                    fieldbackground=palette["surface"],
                    foreground=palette["fg"],
                    insertcolor=palette["fg"],
                    bordercolor=palette["border"])
    style.map("TEntry",
              fieldbackground=[("focus", palette["surface"])])

    # Combobox
    style.configure("TCombobox",
                    fieldbackground=palette["surface"],
                    foreground=palette["fg"],
                    selectbackground=palette["select_bg"],
                    selectforeground=palette["fg"],
                    arrowcolor=palette["fg"])
    # Spinbox
    style.configure("TSpinbox",
                    fieldbackground=palette["surface"],
                    foreground=palette["fg"],
                    bordercolor=palette["border"])

    # Notebook (Tabs)
    style.configure("TNotebook", background=palette["bg"], borderwidth=0)
    style.configure("TNotebook.Tab",
                    background=palette["surface"],
                    foreground=palette["fg_muted"],
                    padding=(10, 6))
    style.map("TNotebook.Tab",
              background=[("selected", palette["bg"])],
              foreground=[("selected", palette["fg"])],
              expand=[("selected", [1, 1, 1, 0])])

    # Separator
    style.configure("TSeparator", background=palette["border"])

    # Treeview
    style.configure("Treeview",
                    background=palette["surface"],
                    foreground=palette["fg"],
                    fieldbackground=palette["surface"],
                    bordercolor=palette["border"],
                    rowheight=26)
    style.map("Treeview",
              background=[("selected", palette["select_bg"])],
              foreground=[("selected", palette["fg"])])
    style.configure("Treeview.Heading",
                    background=palette["surface"],
                    foreground=palette["fg_muted"],
                    relief="flat")
    style.map("Treeview.Heading",
              background=[("active", palette["surface"])],
              relief=[("pressed", "groove")])

    # Alternate row màu nhẹ
    style.layout("Treeview", style.layout("Treeview"))  # ensure layout present

    # Scrollbar
    style.configure("Vertical.TScrollbar",
                    background=palette["surface"],
                    troughcolor=palette["bg"],
                    bordercolor=palette["border"])
    style.configure("Horizontal.TScrollbar",
                    background=palette["surface"],
                    troughcolor=palette["bg"],
                    bordercolor=palette["border"])

    # Cập nhật nền cho widget gốc trong cửa sổ hiện tại
    for w in root.winfo_children():
        try:
            if isinstance(w, (tk.Frame, tk.Toplevel)):
                w.configure(bg=palette["bg"])
        except tk.TclError:
            pass

def toggle_theme(root: tk.Tk | tk.Toplevel) -> str:
    """Đảo light<->dark và trả về mode hiện tại."""
    mode = "dark" if _current_mode == "light" else "light"
    apply_theme(root, mode)
    return mode

def current_mode() -> str:
    return _current_mode
