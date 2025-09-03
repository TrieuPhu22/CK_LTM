# ==================== MODERN THEME & COLORS ====================
class ModernTheme:
    PRIMARY = "#1e3a8a"      # Deep Blue
    SECONDARY = "#3b82f6"    # Bright Blue
    ACCENT = "#f59e0b"       # Orange
    SUCCESS = "#10b981"      # Green
    DANGER = "#ef4444"       # Red
    WARNING = "#f59e0b"      # Yellow
    INFO = "#06b6d4"         # Cyan

    MAIN_BG = "#f8fafc"      # Light Gray
    CARD_BG = "#ffffff"      # White
    SIDEBAR_BG = "#1e293b"   # Dark Blue
    HEADER_BG = "#0f172a"    # Darker Blue

    PRIMARY_TEXT = "#1e293b"
    SECONDARY_TEXT = "#64748b"
    WHITE_TEXT = "#ffffff"
    LIGHT_TEXT = "#94a3b8"

    BORDER = "#e2e8f0"
    HOVER_BORDER = "#cbd5e1"

    TITLE_FONT = ("Segoe UI", 24, "bold")
    HEADER_FONT = ("Segoe UI", 16, "bold")
    SUBHEADER_FONT = ("Segoe UI", 14, "bold")
    BODY_FONT = ("Segoe UI", 11)
    CAPTION_FONT = ("Segoe UI", 10)
    SMALL_FONT = ("Segoe UI", 9)


# Competition IDs
COMPETITIONS = {
    "Premier League": "2021",
    "La Liga": "2014",
    "Bundesliga": "2002",
    "Serie A": "2019",
    "Champions League": "2001",
}

# Connection settings
HOST = "127.0.0.1"
PORT = 65432
FORMAT = "utf8"

# Export & feature flags
EXPORT_DIR = "exports"
DARK_MODE_DEFAULT = False
