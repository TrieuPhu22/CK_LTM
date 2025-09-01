import tkinter as tk
from tkinter import ttk
from modern_theme import ModernTheme

class ModernButton(tk.Button):
    """Custom button với hiệu ứng hover và modern design"""
    def __init__(self, parent, text="", command=None, style="primary", **kwargs):
        self.style = style
        self.setup_colors()
        
        super().__init__(
            parent,
            text=text,
            command=command,
            font=ModernTheme.BODY_FONT,
            relief="flat",
            borderwidth=0,
            cursor="hand2",
            **kwargs
        )
        
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.apply_style()
    
    def setup_colors(self):
        if self.style == "primary":
            self.bg = ModernTheme.PRIMARY
            self.fg = ModernTheme.WHITE_TEXT
            self.hover_bg = ModernTheme.SECONDARY
        elif self.style == "secondary":
            self.bg = ModernTheme.SECONDARY
            self.fg = ModernTheme.WHITE_TEXT
            self.hover_bg = ModernTheme.INFO
        elif self.style == "success":
            self.bg = ModernTheme.SUCCESS
            self.fg = ModernTheme.WHITE_TEXT
            self.hover_bg = "#059669"
        elif self.style == "danger":
            self.bg = ModernTheme.DANGER
            self.fg = ModernTheme.WHITE_TEXT
            self.hover_bg = "#dc2626"
        else:
            self.bg = ModernTheme.BORDER
            self.fg = ModernTheme.PRIMARY_TEXT
            self.hover_bg = ModernTheme.HOVER_BORDER
    
    def apply_style(self):
        self.configure(
            background=self.bg,
            foreground=self.fg,
            activebackground=self.hover_bg,
            activeforeground=self.fg
        )
    
    def on_enter(self, event):
        self.configure(background=self.hover_bg)
    
    def on_leave(self, event):
        self.configure(background=self.bg)

class ModernCard(tk.Frame):
    """Card widget với shadow effect và modern design"""
    def __init__(self, parent, title="", **kwargs):
        super().__init__(
            parent,
            background=ModernTheme.CARD_BG,
            relief="flat",
            borderwidth=1,
            highlightbackground=ModernTheme.BORDER,
            highlightthickness=1,
            **kwargs
        )
        
        if title:
            title_label = tk.Label(
                self,
                text=title,
                font=ModernTheme.SUBHEADER_FONT,
                background=ModernTheme.CARD_BG,
                foreground=ModernTheme.PRIMARY_TEXT,
                anchor="w"
            )
            title_label.pack(fill="x", padx=15, pady=(15, 10))
        
        self.content_frame = tk.Frame(self, background=ModernTheme.CARD_BG)
        self.content_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

class ModernTreeview(ttk.Treeview):
    """Custom Treeview với modern styling"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.setup_style()
    
    def setup_style(self):
        style = ttk.Style()
        
        # Configure Treeview
        style.configure(
            "Modern.Treeview",
            background=ModernTheme.CARD_BG,
            foreground=ModernTheme.PRIMARY_TEXT,
            rowheight=35,
            fieldbackground=ModernTheme.CARD_BG,
            font=ModernTheme.BODY_FONT
        )
        
        # Configure Treeview Heading
        style.configure(
            "Modern.Treeview.Heading",
            background=ModernTheme.PRIMARY,
            foreground=ModernTheme.WHITE_TEXT,
            font=ModernTheme.SUBHEADER_FONT,
            relief="flat"
        )
        
        # Configure selection
        style.map(
            "Modern.Treeview",
            background=[("selected", ModernTheme.SECONDARY)],
            foreground=[("selected", ModernTheme.WHITE_TEXT)]
        )
        
        self.configure(style="Modern.Treeview")

class StatusBar(tk.Frame):
    """Modern status bar"""
    def __init__(self, parent):
        super().__init__(
            parent,
            background=ModernTheme.HEADER_BG,
            height=30
        )
        self.pack(fill="x", side="bottom")
        self.pack_propagate(False)
        
        self.status_label = tk.Label(
            self,
            text="Ready",
            font=ModernTheme.CAPTION_FONT,
            background=ModernTheme.HEADER_BG,
            foreground=ModernTheme.WHITE_TEXT,
            anchor="w"
        )
        self.status_label.pack(side="left", padx=10, pady=5)
        
        # Connection status
        self.connection_label = tk.Label(
            self,
            text="🟢 Connected",
            font=ModernTheme.CAPTION_FONT,
            background=ModernTheme.HEADER_BG,
            foreground=ModernTheme.SUCCESS,
            anchor="e"
        )
        self.connection_label.pack(side="right", padx=10, pady=5)
    
    def update_status(self, message):
        self.status_label.configure(text=message)
    
    def update_connection(self, connected):
        if connected:
            self.connection_label.configure(text="🟢 Connected", foreground=ModernTheme.SUCCESS)
        else:
            self.connection_label.configure(text="🔴 Disconnected", foreground=ModernTheme.DANGER)

