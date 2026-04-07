import tkinter as tk
from tkinter import ttk

class Theme:
    def __init__(self, is_dark: bool = True):
        self.is_dark = is_dark
        self.update_colors()

    def update_colors(self):
        if self.is_dark:
            self.colors = {
                'background': '#0F1117',
                'surface': '#1A1D27',
                'card': '#22263A',
                'primary': '#6C63FF',
                'accent': '#00D2FF',
                'text': '#E8EAF6',
                'subtext': '#8B90A7',
                'border': '#2E3250',
                'success': '#00C897',
                'error': '#FF5370',
                'warning': '#FFB86C'
            }
        else:
            self.colors = {
                'background': '#F4F5FA',
                'surface': '#FFFFFF',
                'card': '#ECEEF8',
                'primary': '#6C63FF',
                'accent': '#0099CC',
                'text': '#1A1D27',
                'subtext': '#5C6080',
                'border': '#D0D3E8',
                'success': '#00A87A',
                'error': '#E53935',
                'warning': '#F57C00'
            }

    def toggle_theme(self):
        self.is_dark = not self.is_dark
        self.update_colors()

    def get_font(self, size: int = 10, bold: bool = False):
        family = "Segoe UI"
        if tk.sys.platform == "darwin":
            family = "SF Pro"
        weight = "bold" if bold else "normal"
        return (family, size, weight)

# Global theme instance
theme = Theme()