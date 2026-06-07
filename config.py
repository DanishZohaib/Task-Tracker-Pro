# Configuration file for TaskTracker Pro

APP_NAME = "TaskTracker Pro"
TAGLINE = "Track. Monitor. Complete."
FOOTER_CREATOR = "Designed & Conceptualized by Danish Zohaib"

# Task Aging Thresholds (in days)
AGING_HIGH_THRESHOLD_DAYS = 7     # > 7 days is High Priority (Very Old)
AGING_MEDIUM_THRESHOLD_DAYS = 3   # > 3 days and <= 7 days is Medium Priority (Old)
# <= 3 days is Normal Priority

# Color Palette for Plotly Charts & General UI elements
COLORS = {
    "primary": "#4F46E5",       # Indigo
    "secondary": "#8B5CF6",     # Purple
    "success": "#10B981",       # Emerald Green (Completed)
    "warning": "#F59E0B",       # Amber (Medium Aging / Pending)
    "danger": "#EF4444",        # Rose/Red (High Aging / Overdue)
    "info": "#3B82F6",          # Blue
    "dark": "#1E293B",          # Slate Dark
    "light": "#F8FAFC",         # Slate Light
    "background_gradient": ["#4F46E5", "#06B6D4"] # Indigo to Cyan
}
