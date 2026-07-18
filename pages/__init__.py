"""Pages package."""
from pages.dashboard import render_dashboard
from pages.analyzer import render_analyzer
from pages.leak_checker import render_leak_checker
from pages.generator import render_generator
from pages.vault import render_vault
from pages.history import render_history
from pages.settings import render_settings
from pages.admin import render_admin

__all__ = [
    "render_dashboard",
    "render_analyzer",
    "render_leak_checker",
    "render_generator",
    "render_vault",
    "render_history",
    "render_settings",
    "render_admin",
]