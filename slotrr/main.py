import tkinter as tk
from tkinter import ttk
from slotrr.auth import auth
from slotrr.db import db
from slotrr.ui.login_screen import LoginScreen
from slotrr.ui.admin.dashboard import AdminDashboard
from slotrr.ui.admin.manage_rooms import ManageRooms
from slotrr.ui.admin.manage_users import ManageUsers
from slotrr.ui.admin.manage_bookings import ManageBookings
from slotrr.ui.admin.campus_map import CampusMap
from slotrr.ui.admin.reports import Reports
from slotrr.ui.teacher.dashboard import TeacherDashboard
from slotrr.ui.teacher.book_room import BookRoom
from slotrr.ui.teacher.my_bookings import MyBookings
from slotrr.ui.components import CustomButton
from .ui.theme import theme
from .config import APP_NAME
import sys

# ── Color palette ────────────────────────────────────────────────
NAV_BG        = "#151B2B"   # dark navy for navbar
NAV_BTN_REST  = "#1E2640"   # subtle dark pill (rest)
NAV_BTN_HOVER = "#263052"   # slightly lighter on hover
NAV_BTN_ACTIVE = "#2563EB"  # professional blue for active page
NAV_BTN_FG    = "#8B93A7"   # muted text for rest
NAV_BTN_FG_A  = "#FFFFFF"   # white text for active


class SlotrrApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("1200x800")
        self.configure(bg=theme.colors['background'])
        self.resizable(True, True)

        self._active_page = "Dashboard"
        self._nav_btns = []

        # Set icon
        try:
            from PIL import Image, ImageTk
            icon = Image.new('RGBA', (32, 32), (37, 99, 235, 255))
            self.iconphoto(True, ImageTk.PhotoImage(icon))
        except ImportError:
            pass

        # Main container
        self.container = tk.Frame(self, bg=theme.colors['background'])
        self.container.pack(fill=tk.BOTH, expand=True)

        # ── Navigation bar ───────────────────────────────────────
        self.nav_frame = tk.Frame(self.container, bg=NAV_BG, height=52)
        self.nav_frame.pack(fill=tk.X, side=tk.TOP)
        self.nav_frame.pack_propagate(False)

        # Logo
        logo_label = tk.Label(self.nav_frame, text="SLOTRR",
                              font=theme.get_font(17, True),
                              fg="#38BDF8", bg=NAV_BG)
        logo_label.pack(side=tk.LEFT, padx=(20, 30))

        # Nav buttons container
        self.nav_buttons = tk.Frame(self.nav_frame, bg=NAV_BG)
        self.nav_buttons.pack(side=tk.LEFT, fill=tk.Y)

        # Right side: user info
        self.user_frame = tk.Frame(self.nav_frame, bg=NAV_BG)
        self.user_frame.pack(side=tk.RIGHT, padx=20)

        # Content frame
        self.content_frame = tk.Frame(self.container, bg=theme.colors['background'])
        self.content_frame.pack(fill=tk.BOTH, expand=True)

        # Start with login
        self.show_login()

    # ── Login / navigation ───────────────────────────────────────

    def show_login(self):
        self.clear_nav()
        self.clear_content()
        login_screen = LoginScreen(self.content_frame, self.on_login_success)
        login_screen.pack(fill=tk.BOTH, expand=True)

    def on_login_success(self):
        self._active_page = "Dashboard"
        self.setup_navigation()
        self.show_dashboard()

    def setup_navigation(self):
        self.clear_nav()
        self._nav_btns = []
        user = auth.get_current_user()

        # User info label
        user_lbl = tk.Label(self.user_frame, text=user['full_name'],
                            font=theme.get_font(11),
                            fg="#CBD5E1", bg=NAV_BG)
        user_lbl.pack(side=tk.LEFT)

        # Logout icon
        logout_lbl = tk.Label(self.user_frame, text="⏻",
                              font=("Arial", 14), fg="#64748B", bg=NAV_BG,
                              cursor="hand2")
        logout_lbl.pack(side=tk.LEFT, padx=(12, 0))
        logout_lbl.bind("<Button-1>", lambda e: self.logout())
        logout_lbl.bind("<Enter>", lambda e: logout_lbl.config(fg="#EF4444"))
        logout_lbl.bind("<Leave>", lambda e: logout_lbl.config(fg="#64748B"))

        # Determine nav items by role
        if auth.is_admin():
            nav_items = [
                ("Dashboard",  self.show_dashboard),
                ("Rooms",      self.show_manage_rooms),
                ("Users",      self.show_manage_users),
                ("Bookings",   self.show_manage_bookings),
                ("Campus Map", self.show_campus_map),
                ("Reports",    self.show_reports),
            ]
        elif auth.is_teacher():
            nav_items = [
                ("Dashboard",   self.show_dashboard),
                ("Book Room",   self.show_book_room),
                ("My Bookings", self.show_my_bookings),
            ]
        else:
            nav_items = []

        for text, command in nav_items:
            is_active = (text == self._active_page)
            bg = NAV_BTN_ACTIVE if is_active else NAV_BTN_REST
            fg = NAV_BTN_FG_A if is_active else NAV_BTN_FG

            btn = tk.Label(self.nav_buttons, text=text,
                           bg=bg, fg=fg,
                           font=theme.get_font(10, True),
                           padx=18, pady=7, cursor="hand2")
            btn.pack(side=tk.LEFT, padx=4, pady=10)
            btn._nav_text = text

            # Click handler
            def on_click(e, t=text, cmd=command):
                self._active_page = t
                cmd()
            btn.bind("<Button-1>", on_click)

            # Hover (skip if active)
            def enter(e, b=btn):
                if b._nav_text != self._active_page:
                    b.config(bg=NAV_BTN_HOVER, fg="#CBD5E1")
            def leave(e, b=btn):
                if b._nav_text != self._active_page:
                    b.config(bg=NAV_BTN_REST, fg=NAV_BTN_FG)
            btn.bind("<Enter>", enter)
            btn.bind("<Leave>", leave)

            self._nav_btns.append(btn)

    def _refresh_nav_active(self):
        """Re-paint nav buttons so only the active one is highlighted."""
        for btn in self._nav_btns:
            if btn._nav_text == self._active_page:
                btn.config(bg=NAV_BTN_ACTIVE, fg=NAV_BTN_FG_A)
            else:
                btn.config(bg=NAV_BTN_REST, fg=NAV_BTN_FG)

    # ── Page navigation ──────────────────────────────────────────

    def show_dashboard(self):
        self._active_page = "Dashboard"
        self._refresh_nav_active()
        self.clear_content()
        if auth.is_admin():
            dashboard = AdminDashboard(self.content_frame)
        else:
            dashboard = TeacherDashboard(self.content_frame)
        dashboard.pack(fill=tk.BOTH, expand=True)

    def show_manage_rooms(self):
        self._active_page = "Rooms"
        self._refresh_nav_active()
        self.clear_content()
        ManageRooms(self.content_frame).pack(fill=tk.BOTH, expand=True)

    def show_manage_users(self):
        self._active_page = "Users"
        self._refresh_nav_active()
        self.clear_content()
        ManageUsers(self.content_frame).pack(fill=tk.BOTH, expand=True)

    def show_manage_bookings(self):
        self._active_page = "Bookings"
        self._refresh_nav_active()
        self.clear_content()
        ManageBookings(self.content_frame).pack(fill=tk.BOTH, expand=True)

    def show_campus_map(self):
        self._active_page = "Campus Map"
        self._refresh_nav_active()
        self.clear_content()
        CampusMap(self.content_frame).pack(fill=tk.BOTH, expand=True)

    def show_reports(self):
        self._active_page = "Reports"
        self._refresh_nav_active()
        self.clear_content()
        Reports(self.content_frame).pack(fill=tk.BOTH, expand=True)

    def show_book_room(self):
        self._active_page = "Book Room"
        self._refresh_nav_active()
        self.clear_content()
        BookRoom(self.content_frame).pack(fill=tk.BOTH, expand=True)

    def show_my_bookings(self):
        self._active_page = "My Bookings"
        self._refresh_nav_active()
        self.clear_content()
        MyBookings(self.content_frame).pack(fill=tk.BOTH, expand=True)

    # ── Misc ─────────────────────────────────────────────────────

    def logout(self):
        auth.logout()
        self.show_login()

    def toggle_theme(self):
        theme.toggle_theme()
        if auth.get_current_user():
            self.setup_navigation()
            self.show_dashboard()
        else:
            self.show_login()

    def clear_nav(self):
        for widget in self.nav_buttons.winfo_children():
            widget.destroy()
        for widget in self.user_frame.winfo_children():
            widget.destroy()

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()


def run():
    print("Starting SLOTRR...")
    print("Default login: just select a role and click Sign In")
    app = SlotrrApp()
    app.mainloop()

if __name__ == "__main__":
    run()