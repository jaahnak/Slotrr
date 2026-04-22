import tkinter as tk
from tkinter import ttk
from slotrr.auth import auth
from slotrr.db import db
from slotrr.ui.components import Toast
from typing import Callable

# ── Color Palette ────────────────────────────────────────────────
BG_NAVY        = "#0B1120"   # Outer background
CARD_NAVY      = "#131C2F"   # Slightly lighter navy for card
BORDER_LIGHT   = "#1E293B"   # Subtle low-opacity border
LOGO_CYAN      = "#22D3EE"   # Cyan for logo
TEXT_WHITE     = "#F8FAFC"
TEXT_MUTED     = "#94A3B8"
INPUT_BG       = "#0B1120"   # Dark fill for inputs
FOCUS_GLOW     = "#38BDF8"   # Sky-blue focus ring
BTN_BLUE       = "#2563EB"
BTN_HOVER      = "#3B82F6"

# ── Custom Components ────────────────────────────────────────────

class ModernEntry(tk.Frame):
    def __init__(self, parent, placeholder, is_password=False, *args, **kwargs):
        super().__init__(parent, bg=INPUT_BG, highlightthickness=1, 
                         highlightbackground=BORDER_LIGHT, padx=12, pady=10)
        self.is_password = is_password
        self.placeholder = placeholder
        self.is_placeholder = True
        self.show_pass = False

        self.entry = tk.Entry(self, bg=INPUT_BG, fg=TEXT_MUTED, 
                              insertbackground="white", relief="flat", 
                              highlightthickness=0, font=("Helvetica", 11))
        self.entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.entry.insert(0, placeholder)

        if is_password:
            self.eye_btn = tk.Label(self, text="👁️", bg=INPUT_BG, fg=TEXT_MUTED, cursor="hand2")
            self.eye_btn.pack(side=tk.RIGHT, padx=2)
            self.eye_btn.bind("<Button-1>", self.toggle_password)

        self.entry.bind("<FocusIn>", self.on_focus)
        self.entry.bind("<FocusOut>", self.on_focus_out)

    def on_focus(self, e):
        self.config(highlightbackground=FOCUS_GLOW)
        if self.is_placeholder:
            self.entry.delete(0, tk.END)
            self.entry.config(fg=TEXT_WHITE)
            if self.is_password and not self.show_pass:
                self.entry.config(show="*")
            self.is_placeholder = False

    def on_focus_out(self, e):
        self.config(highlightbackground=BORDER_LIGHT)
        if not self.entry.get():
            self.is_placeholder = True
            if self.is_password:
                self.entry.config(show="")
            self.entry.insert(0, self.placeholder)
            self.entry.config(fg=TEXT_MUTED)

    def toggle_password(self, e):
        self.show_pass = not self.show_pass
        if not self.is_placeholder:
            self.entry.config(show="" if self.show_pass else "*")
        # Visual cue for eye (using unicode chars or text)
        self.eye_btn.config(text="🙈" if self.show_pass else "👁️")

    def get(self):
        return "" if self.is_placeholder else self.entry.get()

    def set(self, text):
        if self.is_placeholder:
            self.entry.delete(0, tk.END)
            self.entry.config(fg=TEXT_WHITE)
            self.is_placeholder = False
            if self.is_password and not self.show_pass:
                self.entry.config(show="*")
        else:
            self.entry.delete(0, tk.END)
        self.entry.insert(0, text)


class PillSelector(tk.Frame):
    def __init__(self, parent, options, command, *args, **kwargs):
        # Dark track background
        super().__init__(parent, bg=INPUT_BG, padx=4, pady=4, 
                         highlightthickness=1, highlightbackground=BORDER_LIGHT)
        self.options = options
        self.command = command
        self.buttons = []
        self.active_idx = 0
        
        for i, opt in enumerate(options):
            lbl = tk.Label(self, text=opt, font=("Helvetica", 10, "bold"), 
                           fg=TEXT_MUTED, bg=INPUT_BG, padx=20, pady=8, cursor="hand2")
            lbl.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            lbl.bind("<Button-1>", lambda e, idx=i: self.select(idx))
            self.buttons.append(lbl)
            
        self.select(0)
        
    def select(self, idx):
        self.active_idx = idx
        for i, lbl in enumerate(self.buttons):
            if i == idx:
                lbl.config(bg=BTN_BLUE, fg="#FFFFFF")
            else:
                lbl.config(bg=INPUT_BG, fg=TEXT_MUTED)
        self.command(self.options[idx])

    def get(self):
        return self.options[self.active_idx]


class LoginScreen(tk.Frame):
    def __init__(self, parent, on_login_success: Callable):
        super().__init__(parent, bg=BG_NAVY)
        self.on_login_success = on_login_success
        self.create_widgets()

    def create_widgets(self):
        center = tk.Frame(self, bg=BG_NAVY)
        center.place(relx=0.5, rely=0.5, anchor="center")

        # ── Branding ─────────────────────────────────────────────
        logo_lbl = tk.Label(center, text="SLOTRR", font=("Helvetica", 38, "bold"), 
                            fg=LOGO_CYAN, bg=BG_NAVY)
        logo_lbl.pack()

        tagline = tk.Label(center, text="Classroom Booking System", font=("Helvetica", 12), 
                           fg=TEXT_MUTED, bg=BG_NAVY)
        tagline.pack(pady=(0, 24))

        # ── Login Card ───────────────────────────────────────────
        # Tkinter canvas allows us to draw a pseudo-rounded rectangle for the card
        card_w, card_h = 440, 520
        self.card_canvas = tk.Canvas(center, width=card_w, height=card_h, 
                                     bg=BG_NAVY, highlightthickness=0)
        self.card_canvas.pack()

        self._draw_rounded_rect(self.card_canvas, 0, 0, card_w, card_h, r=16, 
                                fill=CARD_NAVY, outline=BORDER_LIGHT)

        # Frame on top of canvas
        form_frame = tk.Frame(self.card_canvas, bg=CARD_NAVY)
        self.card_canvas.create_window(card_w/2, card_h/2, window=form_frame)

        welcome = tk.Label(form_frame, text="Welcome Back", font=("Helvetica", 28, "bold"),
                           fg=TEXT_WHITE, bg=CARD_NAVY)
        welcome.pack(pady=(0, 6))

        subtitle = tk.Label(form_frame, text="Please enter your credentials", font=("Helvetica", 11),
                            fg=TEXT_MUTED, bg=CARD_NAVY)
        subtitle.pack(pady=(0, 24))

        # ── Inputs ───────────────────────────────────────────────
        self.email_entry = ModernEntry(form_frame, "Email Address")
        self.email_entry.pack(fill=tk.X, pady=(0, 16))

        self.password_entry = ModernEntry(form_frame, "Password", is_password=True)
        self.password_entry.pack(fill=tk.X, pady=(0, 24))

        # ── Role Segments ────────────────────────────────────────
        self.role_selector = PillSelector(form_frame, ["Admin", "Teacher", "Student"], 
                                          command=lambda r: None)
        self.role_selector.pack(fill=tk.X, pady=(0, 32))

        # ── Submit Button ────────────────────────────────────────
        self.login_canvas = tk.Canvas(form_frame, height=48, bg=CARD_NAVY,
                                      highlightthickness=0, cursor="hand2")
        self.login_canvas.pack(fill=tk.X)
        self.login_canvas.bind("<Configure>", self._draw_submit_button)
        self.login_canvas.bind("<Button-1>", lambda e: self.login())
        self.login_canvas.bind("<Enter>", self._on_btn_enter)
        self.login_canvas.bind("<Leave>", self._on_btn_leave)
        self._btn_hovered = False

    def _draw_rounded_rect(self, canvas, x1, y1, x2, y2, r=16, **kwargs):
        points = [
            x1+r, y1, x2-r, y1, x2, y1, x2, y1+r,
            x2, y2-r, x2, y2, x2-r, y2, x1+r, y2,
            x1, y2, x1, y2-r, x1, y1+r, x1, y1, x1+r, y1
        ]
        return canvas.create_polygon(points, smooth=True, **kwargs)

    def _draw_submit_button(self, event=None):
        c = self.login_canvas
        c.delete("all")
        self.login_canvas.update_idletasks()
        w = c.winfo_width()
        h = 48
        if w < 2: return

        r = 8
        fill = BTN_HOVER if self._btn_hovered else BTN_BLUE

        points = [
            r, 0, w - r, 0, w, 0, w, r,
            w, h - r, w, h, w - r, h, r, h,
            0, h, 0, h - r, 0, r, 0, 0, r, 0
        ]
        c.create_polygon(points, fill=fill, smooth=True, outline="")
        
        # Text and right arrow icon
        c.create_text(w / 2, h / 2, text="Login    →", font=("Helvetica", 13, "bold"), fill="#FFFFFF")

    def _on_btn_enter(self, event):
        self._btn_hovered = True
        self._draw_submit_button()

    def _on_btn_leave(self, event):
        self._btn_hovered = False
        self._draw_submit_button()

    def login(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()
        role = self.role_selector.get().lower()

        # Custom validation as requested
        if not email or not password:
            Toast.show(self, "Email and password must not be empty.", "error")
            return
            
        if "@" not in email:
            Toast.show(self, "Invalid email format. Must contain '@'.", "error")
            return

        # Authenticate (Bypassed strict conditions as requested)
        # We just grab a default user from the database corresponding to the role
        users = db.get_users_by_role(role)
        if users:
            auth.current_user = users[0]
            Toast.show(self, f"Welcome back, {auth.current_user['full_name']}!", "success")
            self.on_login_success()
        else:
            # Fallback if somehow no user exists for that role
            auth.current_user = {'id': 1, 'email': email, 'full_name': f'Mock {role.capitalize()}', 'role': role}
            Toast.show(self, f"Welcome back, Mock {role.capitalize()}!", "success")
            self.on_login_success()