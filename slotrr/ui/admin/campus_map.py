import tkinter as tk
from tkinter import ttk
from slotrr.db import db
from slotrr.ui.components import Card, CustomButton
from slotrr.ui.theme import theme
from datetime import date, datetime
from typing import Dict

class CampusMap(Card):
    def __init__(self, parent):
        super().__init__(parent)
        self.selected_date = date.today()
        self.create_widgets()
        self.draw_map()

    def create_widgets(self):
        title = tk.Label(self, text="Campus Map", font=theme.get_font(18, True), 
                        fg=theme.colors['text'], bg=theme.colors['card'])
        title.pack(pady=20)

        # Date selector
        date_frame = tk.Frame(self, bg=theme.colors['card'])
        date_frame.pack(fill=tk.X, padx=20, pady=(0, 10))

        tk.Label(date_frame, text="Date:", font=theme.get_font(12), 
                fg=theme.colors['text'], bg=theme.colors['card']).pack(side=tk.LEFT)
        self.date_var = tk.StringVar(value=self.selected_date.isoformat())
        date_entry = ttk.Entry(date_frame, textvariable=self.date_var)
        date_entry.pack(side=tk.LEFT, padx=(5, 10))

        update_btn = CustomButton(date_frame, text="Update", command=self.update_date)
        update_btn.pack(side=tk.LEFT)

        # Canvas for map
        self.canvas = tk.Canvas(self, bg=theme.colors['surface'], highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=20, pady=(10, 20))

        # Legend
        legend_frame = tk.Frame(self, bg=theme.colors['card'])
        legend_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        legends = [
            ("🟢 Available", theme.colors['success']),
            ("🔴 Booked", theme.colors['error']),
            ("🟡 Partially Booked", theme.colors['warning'])
        ]

        for text, color in legends:
            frame = tk.Frame(legend_frame, bg=theme.colors['card'])
            frame.pack(side=tk.LEFT, padx=(0, 20))
            tk.Label(frame, text="■", font=theme.get_font(14), fg=color, bg=theme.colors['card']).pack(side=tk.LEFT)
            tk.Label(frame, text=text, font=theme.get_font(10), fg=theme.colors['text'], bg=theme.colors['card']).pack(side=tk.LEFT)

    def update_date(self):
        try:
            self.selected_date = date.fromisoformat(self.date_var.get())
            self.draw_map()
        except ValueError:
            pass  # Invalid date, ignore

    def draw_map(self):
        self.canvas.delete("all")
        rooms = db.get_all_classrooms()
        bookings = db.get_bookings_for_date(self.selected_date)

        # Create booking lookup
        booking_lookup = {}
        for booking in bookings:
            room_id = booking['room_id']
            if room_id not in booking_lookup:
                booking_lookup[room_id] = []
            booking_lookup[room_id].append(booking)

        # Draw grid
        cols = 5
        rows = (len(rooms) + cols - 1) // cols
        cell_width = 100
        cell_height = 80
        margin = 20

        for i, room in enumerate(rooms):
            x = (i % cols) * (cell_width + margin) + margin
            y = (i // cols) * (cell_height + margin) + margin

            # Determine color
            room_bookings = booking_lookup.get(room['id'], [])
            if not room_bookings:
                color = theme.colors['success']
            elif len(room_bookings) >= 6:  # Assuming 6 time slots per day
                color = theme.colors['error']
            else:
                color = theme.colors['warning']

            # Draw room rectangle
            self.canvas.create_rectangle(x, y, x + cell_width, y + cell_height, 
                                       fill=color, outline=theme.colors['border'], width=2)
            self.canvas.create_text(x + cell_width/2, y + cell_height/2, 
                                  text=room['name'], font=theme.get_font(10, True), 
                                  fill=theme.colors['text'])

            # Bind click event
            self.canvas.tag_bind(self.canvas.create_rectangle(x, y, x + cell_width, y + cell_height, fill="", outline=""), 
                               "<Button-1>", lambda e, r=room, b=room_bookings: self.show_room_details(r, b))

    def show_room_details(self, room: Dict, bookings: list):
        dialog = tk.Toplevel(self)
        dialog.title(f"Room {room['name']}")
        dialog.geometry("500x400")
        dialog.config(bg=theme.colors['background'])

        card = Card(dialog)
        card.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(card, text=f"Room {room['name']}", font=theme.get_font(16, True), 
                fg=theme.colors['text'], bg=theme.colors['card']).pack(pady=10)

        tk.Label(card, text=f"Capacity: {room['capacity']}", font=theme.get_font(12), 
                fg=theme.colors['subtext'], bg=theme.colors['card']).pack(anchor="w", padx=20)
        tk.Label(card, text=f"Floor: {room['floor']}, Building: {room['building']}", font=theme.get_font(12), 
                fg=theme.colors['subtext'], bg=theme.colors['card']).pack(anchor="w", padx=20)

        tk.Label(card, text="Today's Bookings:", font=theme.get_font(14, True), 
                fg=theme.colors['text'], bg=theme.colors['card']).pack(pady=(20, 10))

        if bookings:
            for booking in bookings:
                tk.Label(card, text=f"{booking['start_time']} - {booking['end_time']}: {booking['subject_name']} ({booking['users']['full_name']})", 
                        font=theme.get_font(10), fg=theme.colors['text'], bg=theme.colors['card']).pack(anchor="w", padx=20)
        else:
            tk.Label(card, text="No bookings for today", font=theme.get_font(10), 
                    fg=theme.colors['subtext'], bg=theme.colors['card']).pack(anchor="w", padx=20)