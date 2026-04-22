import tkinter as tk
from tkinter import ttk, messagebox
from slotrr.auth import auth
from slotrr.db import db
from slotrr.email_service import email_service
from slotrr.ui.components import Card, CustomButton, CustomEntry, Toast, LoadingSpinner
from slotrr.ui.theme import theme
from datetime import date, time
from typing import List

class BookRoom(Card):
    def __init__(self, parent):
        super().__init__(parent)
        self.selected_students = []
        self.create_widgets()

    def create_widgets(self):
        title = tk.Label(self, text="Book a Classroom", font=theme.get_font(18, True), 
                        fg=theme.colors['text'], bg=theme.colors['card'])
        title.pack(pady=20)

        # Room selection
        tk.Label(self, text="Select Room", font=theme.get_font(12), 
                fg=theme.colors['text'], bg=theme.colors['card']).pack(anchor="w", padx=20)
        self.room_var = tk.StringVar()
        self.room_combo = ttk.Combobox(self, textvariable=self.room_var, state="readonly")
        self.room_combo.pack(fill=tk.X, padx=20, pady=(5, 15))
        self.load_rooms()

        # Date
        tk.Label(self, text="Date", font=theme.get_font(12), 
                fg=theme.colors['text'], bg=theme.colors['card']).pack(anchor="w", padx=20)
        self.date_var = tk.StringVar(value=date.today().isoformat())
        date_entry = ttk.Entry(self, textvariable=self.date_var)
        date_entry.pack(fill=tk.X, padx=20, pady=(5, 15))

        # Time slot
        tk.Label(self, text="Time Slot", font=theme.get_font(12), 
                fg=theme.colors['text'], bg=theme.colors['card']).pack(anchor="w", padx=20)
        self.time_var = tk.StringVar()
        time_slots = ["9:00–10:00", "10:00–11:00", "11:00–12:00", "12:00–13:00", 
                     "13:00–14:00", "14:00–15:00", "15:00–16:00", "16:00–17:00", "17:00–18:00"]
        time_combo = ttk.Combobox(self, textvariable=self.time_var, values=time_slots, state="readonly")
        time_combo.pack(fill=tk.X, padx=20, pady=(5, 15))

        # Subject
        tk.Label(self, text="Subject Name", font=theme.get_font(12), 
                fg=theme.colors['text'], bg=theme.colors['card']).pack(anchor="w", padx=20)
        self.subject_entry = CustomEntry(self, placeholder="Enter subject name")
        self.subject_entry.pack(fill=tk.X, padx=20, pady=(5, 15))

        # Students
        tk.Label(self, text="Select Students", font=theme.get_font(12), 
                fg=theme.colors['text'], bg=theme.colors['card']).pack(anchor="w", padx=20)
        self.student_var = tk.StringVar()
        self.student_combo = ttk.Combobox(self, textvariable=self.student_var)
        self.student_combo.pack(fill=tk.X, padx=20, pady=(5, 10))
        self.load_students()

        add_student_btn = CustomButton(self, text="Add Student", command=self.add_student)
        add_student_btn.pack(pady=(0, 10))

        self.selected_students_list = tk.Listbox(self, bg=theme.colors['surface'], fg=theme.colors['text'], 
                                                selectbackground=theme.colors['primary'])
        self.selected_students_list.pack(fill=tk.X, padx=20, pady=(0, 15))

        remove_student_btn = CustomButton(self, text="Remove Selected", command=self.remove_student)
        remove_student_btn.pack(pady=(0, 15))

        # Note
        tk.Label(self, text="Note (optional)", font=theme.get_font(12), 
                fg=theme.colors['text'], bg=theme.colors['card']).pack(anchor="w", padx=20)
        self.note_entry = tk.Text(self, height=3, bg=theme.colors['surface'], fg=theme.colors['text'], 
                                 insertbackground=theme.colors['text'])
        self.note_entry.pack(fill=tk.X, padx=20, pady=(5, 20))

        # Book button
        self.book_btn = CustomButton(self, text="Book Room", command=self.book_room, primary=True)
        self.book_btn.pack(pady=(0, 20))

    def load_rooms(self):
        rooms = db.get_all_classrooms()
        self.room_combo['values'] = [f"{room['name']} ({room['id']})" for room in rooms]
        self.room_ids = {f"{room['name']} ({room['id']})": room['id'] for room in rooms}

    def load_students(self):
        students = db.get_users_by_role('student')
        self.student_combo['values'] = [f"{s['full_name']} ({s['email']})" for s in students]
        self.student_data = {f"{s['full_name']} ({s['email']})": s for s in students}

    def add_student(self):
        student_str = self.student_var.get()
        if student_str and student_str not in self.selected_students:
            self.selected_students.append(student_str)
            self.selected_students_list.insert(tk.END, student_str)
            self.student_var.set("")

    def remove_student(self):
        selected = self.selected_students_list.curselection()
        if selected:
            index = selected[0]
            self.selected_students_list.delete(index)
            del self.selected_students[index]

    def book_room(self):
        room_str = self.room_var.get()
        date_str = self.date_var.get()
        time_str = self.time_var.get()
        subject = self.subject_entry.get()
        note = self.note_entry.get("1.0", tk.END).strip()

        if not all([room_str, date_str, time_str, subject]):
            Toast.show(self, "Please fill in all required fields", "error")
            return

        if not self.selected_students:
            Toast.show(self, "Please select at least one student", "warning")
            return

        # Parse inputs
        room_id = self.room_ids[room_str]
        booking_date = date.fromisoformat(date_str)
        start_time_str, end_time_str = time_str.split('–')
        start_time = time.fromisoformat(start_time_str.replace(':', '') + ':00')
        end_time = time.fromisoformat(end_time_str.replace(':', '') + ':00')

        # Check conflict
        existing = db.get_bookings_for_room_date(room_id, booking_date)
        conflict = any(b['start_time'] == start_time.isoformat() and b['end_time'] == end_time.isoformat() for b in existing)
        if conflict:
            Toast.show(self, "Time slot already booked for this room", "error")
            return

        # Create booking
        user = auth.get_current_user()
        booking = db.create_booking(room_id, user['id'], subject, booking_date, start_time, end_time, note)

        # Add students
        student_ids = [self.student_data[s]['id'] for s in self.selected_students]
        db.add_students_to_booking(booking.data[0]['id'], student_ids)

        # Send emails
        room_name = db.get_classroom_name(room_id)
        for student_str in self.selected_students:
            student = self.student_data[student_str]
            email_service.send_lecture_notification(
                student['email'], student['full_name'], user['full_name'], subject,
                room_name, date_str, start_time_str, end_time_str
            )

        # Send to admin
        admins = db.get_users_by_role('admin')
        for admin in admins:
            email_service.send_admin_booking_alert(
                admin['email'], user['full_name'], subject, room_name,
                date_str, start_time_str, end_time_str, [self.student_data[s]['full_name'] for s in self.selected_students]
            )

        Toast.show(self, "Room booked successfully! Emails sent.", "success")
        # Clear form
        self.subject_entry.delete(0, tk.END)
        self.note_entry.delete("1.0", tk.END)
        self.selected_students.clear()
        self.selected_students_list.delete(0, tk.END)