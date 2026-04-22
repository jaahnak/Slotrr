import tkinter as tk
from tkinter import ttk, messagebox
from slotrr.db import db
from slotrr.ui.components import Card, CustomButton, ConfirmationDialog, Toast
from slotrr.ui.theme import theme
from datetime import datetime

class ManageBookings(Card):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()
        self.load_bookings()

    def create_widgets(self):
        title = tk.Label(self, text="Manage Bookings", font=theme.get_font(18, True), 
                        fg=theme.colors['text'], bg=theme.colors['card'])
        title.pack(pady=20)

        # Filters
        filter_frame = tk.Frame(self, bg=theme.colors['card'])
        filter_frame.pack(fill=tk.X, padx=20, pady=(0, 10))

        tk.Label(filter_frame, text="Date:", font=theme.get_font(12), 
                fg=theme.colors['text'], bg=theme.colors['card']).pack(side=tk.LEFT)
        self.date_var = tk.StringVar()
        date_entry = ttk.Entry(filter_frame, textvariable=self.date_var)
        date_entry.pack(side=tk.LEFT, padx=(5, 10))

        filter_btn = CustomButton(filter_frame, text="Filter", command=self.load_bookings)
        filter_btn.pack(side=tk.LEFT)

        # Bookings table
        self.tree = ttk.Treeview(self, columns=("Teacher", "Room", "Subject", "Date", "Time", "Students"), show="headings")
        self.tree.heading("Teacher", text="Teacher")
        self.tree.heading("Room", text="Room")
        self.tree.heading("Subject", text="Subject")
        self.tree.heading("Date", text="Date")
        self.tree.heading("Time", text="Time")
        self.tree.heading("Students", text="Students")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        # Cancel button
        cancel_btn = CustomButton(self, text="Cancel Booking", command=self.cancel_booking)
        cancel_btn.pack(pady=(0, 20))

    def load_bookings(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        date_filter = self.date_var.get() if self.date_var.get() else None
        bookings = db.get_all_bookings(date_filter)

        for booking in bookings:
            students = db.get_students_for_booking(booking['id'])
            student_names = [s['users']['full_name'] for s in students]
            self.tree.insert("", tk.END, values=(
                booking['users']['full_name'],
                booking['classrooms']['name'],
                booking['subject_name'],
                booking['date'],
                f"{booking['start_time']} - {booking['end_time']}",
                ', '.join(student_names)
            ), tags=(booking['id'],))

    def cancel_booking(self):
        selected = self.tree.selection()
        if not selected:
            Toast.show(self, "Please select a booking to cancel", "warning")
            return
        booking_id = self.tree.item(selected[0], 'tags')[0]
        if ConfirmationDialog.ask(self, "Cancel Booking", "Are you sure you want to cancel this booking?"):
            db.cancel_booking(booking_id)
            self.load_bookings()
            Toast.show(self, "Booking cancelled successfully", "success")