import tkinter as tk
from tkinter import ttk
from slotrr.auth import auth
from slotrr.db import db
from slotrr.ui.components import Card, CustomButton
from slotrr.ui.theme import theme

class TeacherDashboard(Card):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()
        self.load_bookings()

    def create_widgets(self):
        title = tk.Label(self, text="Teacher Dashboard", font=theme.get_font(18, True), 
                        fg=theme.colors['text'], bg=theme.colors['card'])
        title.pack(pady=20)

        # Quick actions
        actions_frame = tk.Frame(self, bg=theme.colors['card'])
        actions_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        book_btn = CustomButton(actions_frame, text="Book Room", command=self.book_room, primary=True)
        book_btn.pack(side=tk.LEFT, padx=(0, 10))

        # My bookings
        bookings_label = tk.Label(self, text="My Bookings", font=theme.get_font(14, True), 
                                 fg=theme.colors['text'], bg=theme.colors['card'])
        bookings_label.pack(anchor="w", padx=20, pady=(20, 10))

        self.bookings_tree = ttk.Treeview(self, columns=("Room", "Subject", "Date", "Time"), show="headings")
        self.bookings_tree.heading("Room", text="Room")
        self.bookings_tree.heading("Subject", text="Subject")
        self.bookings_tree.heading("Date", text="Date")
        self.bookings_tree.heading("Time", text="Time")
        self.bookings_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

    def load_bookings(self):
        for item in self.bookings_tree.get_children():
            self.bookings_tree.delete(item)

        user = auth.get_current_user()
        bookings = db.get_user_bookings(user['id'])

        for booking in bookings:
            self.bookings_tree.insert("", tk.END, values=(
                booking['classrooms']['name'],
                booking['subject_name'],
                booking['date'],
                f"{booking['start_time']} - {booking['end_time']}"
            ))

    def book_room(self):
        # This will be handled by the main app navigation
        pass