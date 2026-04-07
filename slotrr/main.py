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

class SlotrrApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("1200x800")
        self.configure(bg=theme.colors['background'])
        self.resizable(True, True)

        # Set icon
        try:
            from PIL import Image, ImageTk
            icon = Image.new('RGBA', (32, 32), (100, 100, 255, 255))
            self.iconphoto(True, ImageTk.PhotoImage(icon))
        except ImportError:
            pass

        # Theme toggle button
        self.theme_btn = tk.Button(self, text="🌙" if theme.is_dark else "☀", command=self.toggle_theme, 
                                  bg=theme.colors['background'], fg=theme.colors['text'], 
                                  font=("Arial", 16), relief="flat", borderwidth=0)
        self.theme_btn.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)

        # Main container
        self.container = tk.Frame(self, bg=theme.colors['background'])
        self.container.pack(fill=tk.BOTH, expand=True)

        # Navigation bar (horizontal top bar)
        self.nav_frame = tk.Frame(self.container, bg=theme.colors['card'], height=50)
        self.nav_frame.pack(fill=tk.X, side=tk.TOP)
        self.nav_frame.pack_propagate(False)

        # Logo
        logo_label = tk.Label(self.nav_frame, text="SLOTRR", font=theme.get_font(16, True), 
                             fg=theme.colors['accent'], bg=theme.colors['card'])
        logo_label.pack(side=tk.LEFT, padx=20)

        # Nav buttons container
        self.nav_buttons = tk.Frame(self.nav_frame, bg=theme.colors['card'])
        self.nav_buttons.pack(side=tk.LEFT, expand=True)

        # User info
        self.user_frame = tk.Frame(self.nav_frame, bg=theme.colors['card'])
        self.user_frame.pack(side=tk.RIGHT, padx=20)

        # Content frame
        self.content_frame = tk.Frame(self.container, bg=theme.colors['background'])
        self.content_frame.pack(fill=tk.BOTH, expand=True)

        # Start with login
        self.show_login()

    def show_login(self):
        self.clear_nav()
        self.clear_content()
        login_screen = LoginScreen(self.content_frame, self.on_login_success)
        login_screen.pack(fill=tk.BOTH, expand=True)

    def on_login_success(self):
        self.setup_navigation()
        self.show_dashboard()

    def setup_navigation(self):
        self.clear_nav()
        user = auth.get_current_user()

        # User info
        name_label = tk.Label(self.user_frame, text=user['full_name'], font=theme.get_font(12), 
                             fg=theme.colors['text'], bg=theme.colors['card'])
        name_label.pack(side=tk.LEFT)

        logout_btn = tk.Button(self.user_frame, text="🚪", command=self.logout, 
                              bg=theme.colors['card'], fg=theme.colors['text'], 
                              font=("Arial", 12), relief="flat", borderwidth=0)
        logout_btn.pack(side=tk.LEFT, padx=(10, 0))

        # Navigation buttons
        nav_items = []
        if auth.is_admin():
            nav_items = [
                ("Dashboard", self.show_dashboard),
                ("Rooms", self.show_manage_rooms),
                ("Users", self.show_manage_users),
                ("Bookings", self.show_manage_bookings),
                ("Campus Map", self.show_campus_map),
                ("Reports", self.show_reports)
            ]
        elif auth.is_teacher():
            nav_items = [
                ("Dashboard", self.show_dashboard),
                ("Book Room", self.show_book_room),
                ("My Bookings", self.show_my_bookings)
            ]

        for text, command in nav_items:
            btn = tk.Button(self.nav_buttons, text=text, command=command, 
                           bg=theme.colors['card'], fg=theme.colors['text'], 
                           font=theme.get_font(10), relief="flat", borderwidth=0)
            btn.pack(side=tk.LEFT, padx=10)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg=theme.colors['primary'], fg=theme.colors['text']))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=theme.colors['card'], fg=theme.colors['text']))

    def show_dashboard(self):
        self.clear_content()
        if auth.is_admin():
            dashboard = AdminDashboard(self.content_frame)
        else:
            dashboard = TeacherDashboard(self.content_frame)
        dashboard.pack(fill=tk.BOTH, expand=True)

    def show_manage_rooms(self):
        self.clear_content()
        manage_rooms = ManageRooms(self.content_frame)
        manage_rooms.pack(fill=tk.BOTH, expand=True)

    def show_manage_users(self):
        self.clear_content()
        manage_users = ManageUsers(self.content_frame)
        manage_users.pack(fill=tk.BOTH, expand=True)

    def show_manage_bookings(self):
        self.clear_content()
        manage_bookings = ManageBookings(self.content_frame)
        manage_bookings.pack(fill=tk.BOTH, expand=True)

    def show_campus_map(self):
        self.clear_content()
        campus_map = CampusMap(self.content_frame)
        campus_map.pack(fill=tk.BOTH, expand=True)

    def show_reports(self):
        self.clear_content()
        reports = Reports(self.content_frame)
        reports.pack(fill=tk.BOTH, expand=True)

    def show_book_room(self):
        self.clear_content()
        book_room = BookRoom(self.content_frame)
        book_room.pack(fill=tk.BOTH, expand=True)

    def show_my_bookings(self):
        self.clear_content()
        my_bookings = MyBookings(self.content_frame)
        my_bookings.pack(fill=tk.BOTH, expand=True)

    def logout(self):
        auth.logout()
        self.show_login()

    def toggle_theme(self):
        theme.toggle_theme()
        self.theme_btn.config(text="🌙" if theme.is_dark else "☀")
        # Re-render current screen
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
    # Check if admin exists, if not, create setup
    admins = db.get_users_by_role('admin')
    if not admins:
        print("No admin user found. Please create one manually in the database.")
        # For demo, create a default admin
        db.create_user("Admin User", "admin@slotrr.com", "admin123", "admin")

    app = SlotrrApp()
    app.mainloop()

if __name__ == "__main__":
    run()