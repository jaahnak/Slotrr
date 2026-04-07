import tkinter as tk
from tkinter import ttk, messagebox
from slotrr.auth import auth
from slotrr.db import db
from slotrr.ui.components import Card, CustomButton, CustomEntry, Toast
from slotrr.ui.theme import theme
from typing import Callable

class LoginScreen(Card):
    def __init__(self, parent, on_login_success: Callable):
        super().__init__(parent)
        self.on_login_success = on_login_success
        self.create_widgets()

    def create_widgets(self):
        # Logo
        logo_label = tk.Label(self, text="SLOTRR", font=theme.get_font(24, True), 
                             fg=theme.colors['accent'], bg=theme.colors['card'])
        logo_label.pack(pady=(50, 20))

        # Email
        email_label = tk.Label(self, text="Email", font=theme.get_font(12), 
                              fg=theme.colors['text'], bg=theme.colors['card'])
        email_label.pack(anchor="w", padx=40)
        self.email_entry = CustomEntry(self, placeholder="Enter your email")
        self.email_entry.pack(fill=tk.X, padx=40, pady=(5, 15))

        # Password
        password_label = tk.Label(self, text="Password", font=theme.get_font(12), 
                                 fg=theme.colors['text'], bg=theme.colors['card'])
        password_label.pack(anchor="w", padx=40)
        self.password_entry = CustomEntry(self, placeholder="Enter your password", show="*")
        self.password_entry.pack(fill=tk.X, padx=40, pady=(5, 15))

        # Role
        role_label = tk.Label(self, text="Role", font=theme.get_font(12), 
                             fg=theme.colors['text'], bg=theme.colors['card'])
        role_label.pack(anchor="w", padx=40)
        self.role_var = tk.StringVar(value="teacher")
        role_combo = ttk.Combobox(self, textvariable=self.role_var, 
                                 values=["admin", "teacher", "student"], state="readonly")
        role_combo.pack(fill=tk.X, padx=40, pady=(5, 20))

        # Login button
        login_btn = CustomButton(self, text="Login", command=self.login, primary=True)
        login_btn.pack(pady=(0, 10))

        # Forgot password
        forgot_label = tk.Label(self, text="Forgot password?", font=theme.get_font(10), 
                               fg=theme.colors['accent'], bg=theme.colors['card'], cursor="hand2")
        forgot_label.pack(pady=(0, 50))
        forgot_label.bind("<Button-1>", lambda e: self.forgot_password())

    def login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        role = self.role_var.get()

        if not email or not password:
            Toast.show(self, "Please fill in all fields", "error")
            return

        if auth.login(email, password, role):
            Toast.show(self, "Login successful!", "success")
            self.on_login_success()
        else:
            Toast.show(self, "Invalid credentials", "error")

    def forgot_password(self):
        messagebox.showinfo("Forgot Password", "Please contact your administrator to reset your password.")