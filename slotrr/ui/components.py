import tkinter as tk
from tkinter import ttk, messagebox
from slotrr.ui.theme import theme
from typing import Callable, Optional

class RoundedFrame(tk.Canvas):
    def __init__(self, parent, radius=10, **kwargs):
        tk.Canvas.__init__(self, parent, **kwargs)
        self.radius = radius
        self.bind("<Configure>", self._draw_rounded_rect)

    def _draw_rounded_rect(self, event=None):
        self.delete("all")
        width = self.winfo_width()
        height = self.winfo_height()
        self.create_rounded_rectangle(0, 0, width, height, radius=self.radius, fill=theme.colors['card'], outline=theme.colors['border'])

    def create_rounded_rectangle(self, x1, y1, x2, y2, radius=10, **kwargs):
        points = [x1+radius, y1,
                  x1+radius, y1,
                  x2-radius, y1,
                  x2-radius, y1,
                  x2, y1,
                  x2, y1+radius,
                  x2, y1+radius,
                  x2, y2-radius,
                  x2, y2-radius,
                  x2, y2,
                  x2-radius, y2,
                  x2-radius, y2,
                  x1+radius, y2,
                  x1+radius, y2,
                  x1, y2,
                  x1, y2-radius,
                  x1, y2-radius,
                  x1, y1+radius,
                  x1, y1+radius,
                  x1, y1]
        return self.create_polygon(points, **kwargs, smooth=True)

class CustomButton(tk.Button):
    def __init__(self, parent, text="", command=None, primary=False, **kwargs):
        super().__init__(parent, text=text, command=command, **kwargs)
        self.primary = primary
        self.config(
            font=theme.get_font(10, True),
            relief="flat",
            borderwidth=0,
            padx=20,
            pady=10,
            cursor="hand2"
        )
        self.update_style()
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def update_style(self):
        if self.primary:
            bg = theme.colors['primary']
            fg = theme.colors['text']
        else:
            bg = theme.colors['surface']
            fg = theme.colors['text']
        self.config(bg=bg, fg=fg, activebackground=theme.colors['accent'], activeforeground=fg)

    def on_enter(self, event):
        self.config(bg=theme.colors['accent'])

    def on_leave(self, event):
        self.update_style()

class CustomEntry(ttk.Entry):
    def __init__(self, parent, placeholder="", **kwargs):
        super().__init__(parent, **kwargs)
        self.placeholder = placeholder
        self.placeholder_color = theme.colors['subtext']
        self.default_color = theme.colors['text']
        self.bind("<FocusIn>", self.on_focus_in)
        self.bind("<FocusOut>", self.on_focus_out)
        self.on_focus_out()

    def on_focus_in(self, event):
        if self.get() == self.placeholder:
            self.delete(0, tk.END)
            self.config(foreground=self.default_color)

    def on_focus_out(self, event):
        if not self.get():
            self.insert(0, self.placeholder)
            self.config(foreground=self.placeholder_color)

class Card(RoundedFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.config(bg=theme.colors['background'], highlightthickness=0)

class Toast:
    @staticmethod
    def show(parent, message: str, type_: str = "info"):
        colors = {
            "success": theme.colors['success'],
            "error": theme.colors['error'],
            "warning": theme.colors['warning'],
            "info": theme.colors['primary']
        }
        color = colors.get(type_, theme.colors['primary'])
        
        toast = tk.Toplevel(parent)
        toast.geometry("300x50+0+0")
        toast.overrideredirect(True)
        toast.attributes("-topmost", True)
        
        frame = tk.Frame(toast, bg=color)
        frame.pack(fill=tk.BOTH, expand=True)
        
        label = tk.Label(frame, text=message, bg=color, fg=theme.colors['text'], font=theme.get_font(10))
        label.pack(pady=10)
        
        # Position at bottom right
        parent.update_idletasks()
        x = parent.winfo_width() - 320
        y = parent.winfo_height() - 70
        toast.geometry(f"+{x}+{y}")
        
        toast.after(3000, toast.destroy)

class LoadingSpinner(tk.Canvas):
    def __init__(self, parent, size=20, **kwargs):
        super().__init__(parent, width=size, height=size, bg=theme.colors['background'], highlightthickness=0, **kwargs)
        self.size = size
        self.angle = 0
        self.draw_spinner()

    def draw_spinner(self):
        self.delete("all")
        center = self.size // 2
        radius = center - 2
        self.create_arc(center-radius, center-radius, center+radius, center+radius, 
                       start=self.angle, extent=270, outline=theme.colors['primary'], width=2)
        self.angle = (self.angle + 10) % 360
        self.after(50, self.draw_spinner)

class ConfirmationDialog:
    @staticmethod
    def ask(parent, title: str, message: str) -> bool:
        return messagebox.askyesno(title, message, parent=parent)