# style_config.py

FONT_FAMILY = "Segoe UI"  # Modern, clean
FONT_SIZE = 11

# Colors: Blue-Eyes White Dragon Mode
COLOR_BG = "#fefefe"           # Almost white, soft on eyes
COLOR_FG = "#111111"           # Deep charcoal (not pitch black)
COLOR_ACCENT = "#62b5e5"       # Cool shimmering light blue
COLOR_BUTTON = "#e2f1fb"       # Soft frosty blue
COLOR_HIGHLIGHT = "#b1e0ff"    # Subtle highlight on hover/active
COLOR_PAGE_BG = "#eaf6ff"  # Light, friendly blue background for pages
COLOR_PROTOCOL = "#B8860B"     # GOLDMEMBER


# Optional extras
COLOR_BORDER = "#b4dfff"       # Light blue for focused input borders
COLOR_PLACEHOLDER = "#888888"  # Slightly faded grey for search bars, etc.

# Styles
STYLE_LABEL = f"""
    color: {COLOR_FG};
    font-family: {FONT_FAMILY};
    font-size: {FONT_SIZE}px;
"""

STYLE_BUTTON = f"""
    background-color: {COLOR_BUTTON};
    color: {COLOR_FG};
    border: 1px solid {COLOR_ACCENT};
    padding: 5px;
    border-radius: 5px;
    font-weight: bold;
"""
