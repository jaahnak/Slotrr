import tkinter as tk
from tkinter import ttk
from slotrr.db import db
from slotrr.ui.components import Card, CustomButton
from slotrr.ui.theme import theme
from typing import List, Dict

class AdminDashboard(Card):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()
        self.load_stats()

    def create_widgets(self):
        title = tk.Label(self, text="Admin Dashboard", font=theme.get_font(18, True), 
                        fg=theme.colors['text'], bg=theme.colors['card'])
        title.pack(pady=20)

        # Stats cards
        self.stats_frame = tk.Frame(self, bg=theme.colors['card'])
        self.stats_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        # Recent bookings
        recent_label = tk.Label(self, text="Recent Bookings", font=theme.get_font(14, True), 
                               fg=theme.colors['text'], bg=theme.colors['card'])
        recent_label.pack(anchor="w", padx=20, pady=(20, 10))

        self.bookings_tree = ttk.Treeview(self, columns=("Teacher", "Room", "Subject", "Date", "Time"), show="headings")
        self.bookings_tree.heading("Teacher", text="Teacher")
        self.bookings_tree.heading("Room", text="Room")
        self.bookings_tree.heading("Subject", text="Subject")
        self.bookings_tree.heading("Date", text="Date")
        self.bookings_tree.heading("Time", text="Time")
        self.bookings_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

    def load_stats(self):
        stats = db.get_stats()
        
        # Clear previous stats
        for widget in self.stats_frame.winfo_children():
            widget.destroy()

        stat_items = [
            ("Total Rooms", stats['total_rooms']),
            ("Active Bookings Today", stats['active_bookings_today']),
            ("Total Teachers", stats['total_teachers']),
            ("Total Students", stats['total_students'])
        ]

        for i, (label, value) in enumerate(stat_items):
            card = Card(self.stats_frame, height=80)
            card.grid(row=0, column=i, padx=10, pady=10, sticky="ew")
            self.stats_frame.grid_columnconfigure(i, weight=1)

            tk.Label(card, text=str(value), font=theme.get_font(24, True), 
                    fg=theme.colors['primary'], bg=theme.colors['card']).pack(pady=(10, 0))
            tk.Label(card, text=label, font=theme.get_font(10), 
                    fg=theme.colors['subtext'], bg=theme.colors['card']).pack()

        # Load recent bookings
        for item in self.bookings_tree.get_children():
            self.bookings_tree.delete(item)

        # Get recent bookings (last 10)
        recent_bookings = db.client.table('bookings').select('*, users(full_name), classrooms(name)').order('created_at', desc=True).limit(10).execute().data

        for booking in recent_bookings:
            self.bookings_tree.insert("", tk.END, values=(
                booking['users']['full_name'],
                booking['classrooms']['name'],
                booking['subject_name'],
                booking['date'],
                f"{booking['start_time']} - {booking['end_time']}"
            ))