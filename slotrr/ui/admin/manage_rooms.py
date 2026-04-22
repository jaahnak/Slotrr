import tkinter as tk
from tkinter import ttk, messagebox
from slotrr.db import db
from slotrr.ui.components import Card, CustomButton, CustomEntry, ConfirmationDialog, Toast
from slotrr.ui.theme import theme

class ManageRooms(Card):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()
        self.load_rooms()

    def create_widgets(self):
        title = tk.Label(self, text="Manage Rooms", font=theme.get_font(18, True), 
                        fg=theme.colors['text'], bg=theme.colors['card'])
        title.pack(pady=20)

        # Add room button
        add_btn = CustomButton(self, text="Add Room", command=self.add_room, primary=True)
        add_btn.pack(pady=(0, 20))

        # Rooms table
        self.tree = ttk.Treeview(self, columns=("Name", "Capacity", "Floor", "Building", "Active"), show="headings")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Capacity", text="Capacity")
        self.tree.heading("Floor", text="Floor")
        self.tree.heading("Building", text="Building")
        self.tree.heading("Active", text="Active")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        # Action buttons
        btn_frame = tk.Frame(self, bg=theme.colors['card'])
        btn_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        edit_btn = CustomButton(btn_frame, text="Edit", command=self.edit_room)
        edit_btn.pack(side=tk.LEFT, padx=(0, 10))

        delete_btn = CustomButton(btn_frame, text="Delete", command=self.delete_room)
        delete_btn.pack(side=tk.LEFT)

    def load_rooms(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        rooms = db.get_all_classrooms_including_inactive()
        for room in rooms:
            self.tree.insert("", tk.END, values=(
                room['name'],
                room['capacity'],
                room['floor'],
                room['building'],
                "Yes" if room['is_active'] else "No"
            ), tags=(room['id'],))

    def add_room(self):
        self.room_dialog("Add Room")

    def edit_room(self):
        selected = self.tree.selection()
        if not selected:
            Toast.show(self, "Please select a room to edit", "warning")
            return
        room_id = self.tree.item(selected[0], 'tags')[0]
        self.room_dialog("Edit Room", room_id)

    def delete_room(self):
        selected = self.tree.selection()
        if not selected:
            Toast.show(self, "Please select a room to delete", "warning")
            return
        room_id = self.tree.item(selected[0], 'tags')[0]
        if ConfirmationDialog.ask(self, "Delete Room", "Are you sure you want to delete this room?"):
            db.delete_classroom(room_id)
            self.load_rooms()
            Toast.show(self, "Room deleted successfully", "success")

    def room_dialog(self, title, room_id=None):
        dialog = tk.Toplevel(self)
        dialog.title(title)
        dialog.geometry("500x520")
        dialog.config(bg=theme.colors['background'])

        card = Card(dialog)
        card.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(card, text=title, font=theme.get_font(16, True), 
                fg=theme.colors['text'], bg=theme.colors['card']).pack(pady=20)

        # Name
        tk.Label(card, text="Name", font=theme.get_font(12), 
                fg=theme.colors['text'], bg=theme.colors['card']).pack(anchor="w")
        name_entry = CustomEntry(card)
        name_entry.pack(fill=tk.X, pady=(5, 15))

        # Capacity
        tk.Label(card, text="Capacity", font=theme.get_font(12), 
                fg=theme.colors['text'], bg=theme.colors['card']).pack(anchor="w")
        capacity_entry = CustomEntry(card)
        capacity_entry.pack(fill=tk.X, pady=(5, 15))

        # Floor
        tk.Label(card, text="Floor", font=theme.get_font(12), 
                fg=theme.colors['text'], bg=theme.colors['card']).pack(anchor="w")
        floor_entry = ttk.Combobox(card, values=["1", "2", "3", "4", "5"], state="readonly")
        floor_entry.pack(fill=tk.X, pady=(5, 15))
        if not room_id:
            floor_entry.set("1")  # Default to 1

        # Building
        tk.Label(card, text="Building", font=theme.get_font(12), 
                fg=theme.colors['text'], bg=theme.colors['card']).pack(anchor="w")
        building_entry = ttk.Combobox(card, values=["Main Block", "Science Block", "Arts Block"], state="readonly")
        building_entry.pack(fill=tk.X, pady=(5, 15))
        if not room_id:
            building_entry.set("Main Block")

        if room_id:
            room = db.get_classroom_by_id(room_id)
            name_entry.insert(0, room['name'])
            capacity_entry.insert(0, str(room['capacity']))
            floor_entry.set(str(room['floor']))
            building_entry.set(room['building'])

        def save():
            name = name_entry.get()
            capacity = int(capacity_entry.get())
            floor = int(floor_entry.get())
            building = building_entry.get()

            if room_id:
                db.update_classroom(room_id, {
                    'name': name,
                    'capacity': capacity,
                    'floor': floor,
                    'building': building
                })
            else:
                db.create_classroom(name, capacity, floor, building)

            self.load_rooms()
            dialog.destroy()
            Toast.show(self, f"Room {'updated' if room_id else 'added'} successfully", "success")

        save_btn = CustomButton(card, text="Save", command=save, primary=True)
        save_btn.pack(pady=20)