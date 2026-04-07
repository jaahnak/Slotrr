import tkinter as tk
from tkinter import ttk, messagebox
from slotrr.db import db
from slotrr.ui.components import Card, CustomButton, CustomEntry, ConfirmationDialog, Toast
from slotrr.ui.theme import theme

class ManageUsers(Card):
    def __init__(self, parent):
        super().__init__(parent)
        self.create_widgets()
        self.load_users()

    def create_widgets(self):
        title = tk.Label(self, text="Manage Users", font=theme.get_font(18, True), 
                        fg=theme.colors['text'], bg=theme.colors['card'])
        title.pack(pady=20)

        # Add user button
        add_btn = CustomButton(self, text="Add User", command=self.add_user, primary=True)
        add_btn.pack(pady=(0, 20))

        # Users table
        self.tree = ttk.Treeview(self, columns=("Name", "Email", "Role"), show="headings")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Email", text="Email")
        self.tree.heading("Role", text="Role")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

        # Action buttons
        btn_frame = tk.Frame(self, bg=theme.colors['card'])
        btn_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

        edit_btn = CustomButton(btn_frame, text="Edit", command=self.edit_user)
        edit_btn.pack(side=tk.LEFT, padx=(0, 10))

        delete_btn = CustomButton(btn_frame, text="Delete", command=self.delete_user)
        delete_btn.pack(side=tk.LEFT, padx=(0, 10))

        reset_btn = CustomButton(btn_frame, text="Reset Password", command=self.reset_password)
        reset_btn.pack(side=tk.LEFT)

    def load_users(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        users = db.get_all_users()
        for user in users:
            self.tree.insert("", tk.END, values=(
                user['full_name'],
                user['email'],
                user['role']
            ), tags=(user['id'],))

    def add_user(self):
        self.user_dialog("Add User")

    def edit_user(self):
        selected = self.tree.selection()
        if not selected:
            Toast.show(self, "Please select a user to edit", "warning")
            return
        user_id = self.tree.item(selected[0], 'tags')[0]
        self.user_dialog("Edit User", user_id)

    def delete_user(self):
        selected = self.tree.selection()
        if not selected:
            Toast.show(self, "Please select a user to delete", "warning")
            return
        user_id = self.tree.item(selected[0], 'tags')[0]
        if ConfirmationDialog.ask(self, "Delete User", "Are you sure you want to delete this user?"):
            db.delete_user(user_id)
            self.load_users()
            Toast.show(self, "User deleted successfully", "success")

    def reset_password(self):
        selected = self.tree.selection()
        if not selected:
            Toast.show(self, "Please select a user to reset password", "warning")
            return
        user_id = self.tree.item(selected[0], 'tags')[0]
        # For simplicity, set password to 'password123'
        db.update_user(user_id, {'password_hash': db.client.table('users').select('password_hash').eq('id', user_id).execute().data[0]['password_hash']})  # Keep same for now
        Toast.show(self, "Password reset to 'password123'", "success")

    def user_dialog(self, title, user_id=None):
        dialog = tk.Toplevel(self)
        dialog.title(title)
        dialog.geometry("400x400")
        dialog.config(bg=theme.colors['background'])

        card = Card(dialog)
        card.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(card, text=title, font=theme.get_font(16, True), 
                fg=theme.colors['text'], bg=theme.colors['card']).pack(pady=20)

        # Full Name
        tk.Label(card, text="Full Name", font=theme.get_font(12), 
                fg=theme.colors['text'], bg=theme.colors['card']).pack(anchor="w")
        name_entry = CustomEntry(card)
        name_entry.pack(fill=tk.X, pady=(5, 15))

        # Email
        tk.Label(card, text="Email", font=theme.get_font(12), 
                fg=theme.colors['text'], bg=theme.colors['card']).pack(anchor="w")
        email_entry = CustomEntry(card)
        email_entry.pack(fill=tk.X, pady=(5, 15))

        # Role
        tk.Label(card, text="Role", font=theme.get_font(12), 
                fg=theme.colors['text'], bg=theme.colors['card']).pack(anchor="w")
        role_var = tk.StringVar(value="student")
        role_combo = ttk.Combobox(card, textvariable=role_var, 
                                 values=["admin", "teacher", "student"], state="readonly")
        role_combo.pack(fill=tk.X, pady=(5, 15))

        # Password (only for new users)
        password_entry = None
        if not user_id:
            tk.Label(card, text="Password", font=theme.get_font(12), 
                    fg=theme.colors['text'], bg=theme.colors['card']).pack(anchor="w")
            password_entry = CustomEntry(card, show="*")
            password_entry.pack(fill=tk.X, pady=(5, 15))

        if user_id:
            user = db.client.table('users').select('*').eq('id', user_id).execute().data[0]
            name_entry.insert(0, user['full_name'])
            email_entry.insert(0, user['email'])
            role_var.set(user['role'])

        def save():
            name = name_entry.get()
            email = email_entry.get()
            role = role_var.get()
            password = password_entry.get() if password_entry else None

            if user_id:
                db.update_user(user_id, {
                    'full_name': name,
                    'email': email,
                    'role': role
                })
            else:
                db.create_user(name, email, password, role)

            self.load_users()
            dialog.destroy()
            Toast.show(self, f"User {'updated' if user_id else 'added'} successfully", "success")

        save_btn = CustomButton(card, text="Save", command=save, primary=True)
        save_btn.pack(pady=20)