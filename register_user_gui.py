import mysql.connector
import bcrypt
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter as tk
from db_config import db_host, db_user, db_password, db_name


class RegisterUserWindow(ttk.Frame):
    def __init__(self, parent, on_success_callback, show_error_message_callback):
        super().__init__(parent, padding=20)
        self.parent = parent
        self.on_success_callback = on_success_callback
        self.show_error_message_callback = show_error_message_callback

        ttk.Label(self, text="Create New User", font=("Helvetica", 18, "bold")).pack(pady=10)

        form_frame = ttk.Frame(self)
        form_frame.pack(pady=10)

        ttk.Label(form_frame, text="Username (required):").grid(row=0, column=0, sticky="e", pady=5)
        self.username_entry = ttk.Entry(form_frame)
        self.username_entry.grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(form_frame, text="Password (required):").grid(row=1, column=0, sticky="e", pady=5)
        self.password_entry = ttk.Entry(form_frame, show="*")
        self.password_entry.grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(form_frame, text="Email (required):").grid(row=2, column=0, sticky="e", pady=5)
        self.email_entry = ttk.Entry(form_frame)
        self.email_entry.grid(row=2, column=1, padx=10, pady=5)

        button_frame = ttk.Frame(self)
        button_frame.pack(pady=15)

        register_btn = ttk.Button(button_frame, text="Register", bootstyle=SUCCESS, command=self.register_user)
        register_btn.grid(row=0, column=0, padx=10)

        back_btn = ttk.Button(button_frame, text="Back to Login", bootstyle=SECONDARY, command=self.back_to_login)
        back_btn.grid(row=0, column=1, padx=10)

        self.username_entry.focus_set()

        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus_set())
        self.password_entry.bind("<Return>", lambda e: self.email_entry.focus_set())
        self.email_entry.bind("<Return>", lambda e: self.register_user())

    def register_user(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        email = self.email_entry.get().strip()

        if not username or not password or not email:
            self.show_error_message_callback("All fields are required.")
            return

        hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

        try:
            conn = mysql.connector.MySQLConnection(
                host=db_host,
                user=db_user,
                password=db_password,
                database=db_name
            )
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, email))
            if cursor.fetchone():
                self.show_error_message_callback("Username or Email already exists.")
                conn.close()
                return

            cursor.execute(
                "INSERT INTO users (username, password, email) VALUES (%s, %s, %s)",
                (username, hashed_password, email)
            )
            conn.commit()
            conn.close()

            self.on_success_callback()

        except Exception as e:
            self.show_error_message_callback(f"Error: {e}")

    def back_to_login(self):
        self.destroy()
        from finance_manager_gui import FinanceManagerApp
        app = FinanceManagerApp(self.parent)
