import tkinter as tk
from tkinter import ttk
from slotrr.db import db
from slotrr.ui.components import Card, CustomButton
from slotrr.ui.theme import theme
from collections import Counter

class Reports(Card):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()
        self.generate_report()

    def create_widgets(self):
        title = tk.Label(self, text="Reports & Analytics", font=theme.get_font(18, True), 
                        fg=theme.colors['text'], bg=theme.colors['card'])
        title.pack(pady=20)

        # Report type selector
        report_frame = tk.Frame(self, bg=theme.colors['card'])
        report_frame.pack(fill=tk.X, padx=20, pady=(0, 10))

        tk.Label(report_frame, text="Report Type:", font=theme.get_font(12), 
                fg=theme.colors['text'], bg=theme.colors['card']).pack(side=tk.LEFT)
        self.report_var = tk.StringVar(value="most_booked_rooms")
        report_combo = ttk.Combobox(report_frame, textvariable=self.report_var, 
                                   values=["most_booked_rooms", "teacher_activity"], state="readonly")
        report_combo.pack(side=tk.LEFT, padx=(5, 10))
        report_combo.bind("<<ComboboxSelected>>", lambda e: self.generate_report())

        # Canvas for chart
        self.canvas = tk.Canvas(self, bg=theme.colors['surface'], highlightthickness=0, height=300)
        self.canvas.pack(fill=tk.X, padx=20, pady=(10, 20))

        # Export button
        export_btn = CustomButton(self, text="Export to CSV", command=self.export_csv)
        export_btn.pack(pady=(0, 20))

    def generate_report(self):
        self.canvas.delete("all")
        report_type = self.report_var.get()

        if report_type == "most_booked_rooms":
            self.draw_bar_chart()
        elif report_type == "teacher_activity":
            self.draw_teacher_chart()

    def draw_bar_chart(self):
        # Get booking counts per room
        bookings = db.get_all_bookings_with_room()
        room_counts = Counter(booking['room_id'] for booking in bookings)
        
        # Get room names
        room_names = {}
        for booking in bookings:
            room_names[booking['room_id']] = booking['classrooms']['name']

        # Sort by count
        sorted_rooms = sorted(room_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        if not sorted_rooms:
            self.canvas.create_text(250, 150, text="No data available", font=theme.get_font(12), fill=theme.colors['text'])
            return

        max_count = max(count for _, count in sorted_rooms)
        bar_width = 30
        spacing = 40
        start_x = 50
        start_y = 250

        for i, (room_id, count) in enumerate(sorted_rooms):
            x = start_x + i * (bar_width + spacing)
            height = (count / max_count) * 200 if max_count > 0 else 0
            self.canvas.create_rectangle(x, start_y - height, x + bar_width, start_y, 
                                       fill=theme.colors['primary'], outline=theme.colors['border'])
            self.canvas.create_text(x + bar_width/2, start_y - height - 10, 
                                  text=str(count), font=theme.get_font(8), fill=theme.colors['text'])
            self.canvas.create_text(x + bar_width/2, start_y + 15, 
                                  text=room_names.get(room_id, 'Unknown'), font=theme.get_font(8), 
                                  fill=theme.colors['text'], angle=45)

        # Title
        self.canvas.create_text(250, 20, text="Most Booked Rooms", font=theme.get_font(14, True), fill=theme.colors['text'])

    def draw_teacher_chart(self):
        # Similar to above, but for teachers
        bookings = db.get_all_bookings_with_teacher()
        teacher_counts = Counter(booking['teacher_id'] for booking in bookings)
        
        teacher_names = {}
        for booking in bookings:
            teacher_names[booking['teacher_id']] = booking['users']['full_name']

        sorted_teachers = sorted(teacher_counts.items(), key=lambda x: x[1], reverse=True)[:10]

        if not sorted_teachers:
            self.canvas.create_text(250, 150, text="No data available", font=theme.get_font(12), fill=theme.colors['text'])
            return

        max_count = max(count for _, count in sorted_teachers)
        bar_width = 30
        spacing = 40
        start_x = 50
        start_y = 250

        for i, (teacher_id, count) in enumerate(sorted_teachers):
            x = start_x + i * (bar_width + spacing)
            height = (count / max_count) * 200 if max_count > 0 else 0
            self.canvas.create_rectangle(x, start_y - height, x + bar_width, start_y, 
                                       fill=theme.colors['accent'], outline=theme.colors['border'])
            self.canvas.create_text(x + bar_width/2, start_y - height - 10, 
                                  text=str(count), font=theme.get_font(8), fill=theme.colors['text'])
            self.canvas.create_text(x + bar_width/2, start_y + 15, 
                                  text=teacher_names.get(teacher_id, 'Unknown'), font=theme.get_font(8), 
                                  fill=theme.colors['text'], angle=45)

        self.canvas.create_text(250, 20, text="Teacher Booking Activity", font=theme.get_font(14, True), fill=theme.colors['text'])

    def export_csv(self):
        # Simple CSV export
        import csv
        report_type = self.report_var.get()
        filename = f"{report_type}.csv"
        
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            if report_type == "most_booked_rooms":
                writer.writerow(["Room", "Bookings"])
                bookings = db.get_all_bookings_with_room()
                room_counts = Counter(booking['room_id'] for booking in bookings)
                room_names = {b['room_id']: b['classrooms']['name'] for b in bookings}
                for room_id, count in room_counts.items():
                    writer.writerow([room_names.get(room_id, 'Unknown'), count])
            elif report_type == "teacher_activity":
                writer.writerow(["Teacher", "Bookings"])
                bookings = db.get_all_bookings_with_teacher()
                teacher_counts = Counter(booking['teacher_id'] for booking in bookings)
                teacher_names = {b['teacher_id']: b['users']['full_name'] for b in bookings}
                for teacher_id, count in teacher_counts.items():
                    writer.writerow([teacher_names.get(teacher_id, 'Unknown'), count])

        tk.messagebox.showinfo("Export Complete", f"Report exported to {filename}")