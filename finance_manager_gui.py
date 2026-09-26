import mysql.connector
import bcrypt
import tkinter as tk
import random

from db_config import db_host, db_user, db_password, db_name
from balance_updater import apply_monthly_update
from savings_manager import calculate_monthly_savings
from fixed_deposits import update_fd_interest_if_due
from transactions_gui import TransactionsWindow
from register_user_gui import RegisterUserWindow
from savings_graph_gui import SavingsGraphWindow  

import ttkbootstrap as ttk
from ttkbootstrap.constants import *


class FinanceManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Finance Manager")
        self.root.minsize(900, 600)
        self.user_id = None

        # ttkbootstrap theme
        self.style = ttk.Style(theme="cyborg")

        # Quotes
        self.quotes = [
            "Beware of little expenses; a small leak will sink a great ship. - Benjamin Franklin",
            "Do not save what is left after spending; instead spend what is left after saving. - Warren Buffett",
            "Small amounts saved consistently grow into great wealth. - Unknown",
        ]
        self.recent_quotes = []

        # Sidebar state
        self.sidebar_visible = True
        self.sidebar_width = 200

        # Show login first
        self.show_login_screen()

    def clear_content_frame(self):
        if hasattr(self, 'content_frame'):
            for widget in self.content_frame.winfo_children():
                widget.destroy()

    # ---------------- LOGIN ----------------
    def show_login_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        frame = ttk.Frame(self.root, padding=30)
        frame.place(relx=0.5, rely=0.5, anchor="center")  # ✅ centered

        ttk.Label(frame, text="Login", font=("Helvetica", 20, "bold")).grid(row=0, column=0, columnspan=2, pady=20)

        ttk.Label(frame, text="Username:").grid(row=1, column=0, sticky="e")
        self.username_entry = ttk.Entry(frame)
        self.username_entry.grid(row=1, column=1, padx=10)

        ttk.Label(frame, text="Password:").grid(row=2, column=0, sticky="e")
        self.password_entry = ttk.Entry(frame, show="*")
        self.password_entry.grid(row=2, column=1, padx=10)

        login_btn = ttk.Button(frame, text="Login", bootstyle=PRIMARY, command=self.handle_login)
        login_btn.grid(row=3, column=0, columnspan=2, pady=20)

        register_btn = ttk.Button(frame, text="Create New User", bootstyle=INFO, command=self.handle_register)
        register_btn.grid(row=4, column=0, columnspan=2)

        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus_set())
        self.password_entry.bind("<Return>", lambda e: self.handle_login())

    def handle_register(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        def on_success():
            self.show_floating_message("New user registered! Please login.", color="#00ff88")
            self.show_login_screen()

        register_frame = RegisterUserWindow(self.root, on_success, self.show_error_message)
        register_frame.place(relx=0.5, rely=0.5, anchor="center")  # ✅ centered

    def handle_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        success, uid = self.authenticate_user(username, password)
        if success:
            self.user_id = uid
            apply_monthly_update(self.user_id)
            calculate_monthly_savings(self.user_id)
            update_fd_interest_if_due(self.user_id)
            self.show_main_menu()
            self.show_home_screen()
            self.show_floating_message(f"Welcome, {username}!")
        else:
            self.show_error_message("Invalid username or password.")

    def authenticate_user(self, username, password):
        conn = mysql.connector.MySQLConnection(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name
        )
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, password FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if result:
            uid, hashed = result
            if bcrypt.checkpw(password.encode(), hashed.encode()):
                return True, uid
        return False, None

    # ---------------- MAIN MENU ----------------
    def show_main_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.container = ttk.Frame(self.root)
        self.container.pack(fill='both', expand=True)

        self.sidebar_frame = ttk.Frame(self.container, width=self.sidebar_width, bootstyle="dark")
        self.sidebar_frame.pack(side='left', fill='y')
        self.sidebar_frame.pack_propagate(False)

        self.content_frame = ttk.Frame(self.container)
        self.content_frame.pack(side='left', fill='both', expand=True)

        ttk.Label(self.sidebar_frame, text="Main Menu", font=("Helvetica", 16, "bold")).pack(pady=20)
        ttk.Button(self.sidebar_frame, text="Home", width=20, bootstyle=PRIMARY, command=self.show_home_screen).pack(pady=5)
        ttk.Button(self.sidebar_frame, text="Transactions", width=20, bootstyle=PRIMARY, command=self.handle_transactions).pack(pady=5)
        ttk.Button(self.sidebar_frame, text="Manage Debts", width=20, bootstyle=SECONDARY, command=self.handle_debts).pack(pady=5)
        ttk.Button(self.sidebar_frame, text="Savings", width=20, bootstyle=SUCCESS, command=self.handle_savings).pack(pady=5)
        ttk.Button(self.sidebar_frame, text="Fixed Deposits", width=20, bootstyle=WARNING, command=self.handle_fd).pack(pady=5)
        ttk.Button(self.sidebar_frame, text="Savings Graph", width=20, bootstyle=INFO, command=self.handle_savings_graph).pack(pady=5)
        ttk.Button(self.sidebar_frame, text="Themes", width=20, bootstyle=INFO, command=self.show_themes_screen).pack(pady=5)
        ttk.Button(self.sidebar_frame, text="Logout", width=20, bootstyle=DANGER, command=self.show_login_screen).pack(pady=5)

        self.toggle_button = ttk.Button(self.sidebar_frame, text="◀", width=3, command=self.toggle_sidebar)
        self.toggle_button.pack(side="bottom", pady=10)

    # ✅ Smooth Sidebar
    def toggle_sidebar(self):
        target_width = 0 if self.sidebar_visible else self.sidebar_width
        current_width = self.sidebar_frame.winfo_width()
        step = -4 if self.sidebar_visible else 4  # smaller step = smoother

        def animate():
            nonlocal current_width
            if (step < 0 and current_width > target_width) or (step > 0 and current_width < target_width):
                current_width += step
                self.sidebar_frame.config(width=current_width)
                self.container.update_idletasks()
                self.root.after(5, animate)
            else:
                self.sidebar_frame.config(width=target_width)
                self.sidebar_visible = not self.sidebar_visible
                self.toggle_button.config(text="▶" if not self.sidebar_visible else "◀")

        animate()

    # ---------------- HOME ----------------
    def show_home_screen(self):
        self.clear_content_frame()

        frame = ttk.Frame(self.content_frame)
        frame.place(relx=0.5, rely=0.5, anchor="center")  # ✅ centered

        balance = self.get_total_balance()

        ttk.Label(frame, text="Finance Manager", font=("Helvetica", 16, "bold")).pack(pady=10)

        quote = self.get_random_quote()
        ttk.Label(frame, text=quote, font=("Helvetica", 10, "italic"), wraplength=500, justify="center").pack(pady=5)

        balance_label = ttk.Label(frame, text=f"Total Balance: ₹{balance:.2f}", font=("Helvetica", 12, "bold"), bootstyle=SUCCESS)
        balance_label.pack(pady=10)

        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=20)

        buttons = [
            ("Transactions", self.handle_transactions, PRIMARY),
            ("Manage Debts", self.handle_debts, SECONDARY),
            ("Savings", self.handle_savings, SUCCESS),
            ("Fixed Deposits", self.handle_fd, WARNING)
        ]

        for idx, (text, command, style) in enumerate(buttons):
            btn = ttk.Button(button_frame, text=text, width=15, bootstyle=style, command=command)
            btn.grid(row=idx // 2, column=idx % 2, padx=10, pady=10)

        credit_btn = ttk.Button(frame, text="Credits", command=self.show_credit_info, bootstyle=INFO)
        credit_btn.pack(pady=10)

    def get_random_quote(self):
        available_quotes = [q for q in self.quotes if q not in self.recent_quotes]
        if not available_quotes:
            self.recent_quotes.clear()
            available_quotes = self.quotes.copy()

        quote = random.choice(available_quotes)
        self.recent_quotes.append(quote)

        if len(self.recent_quotes) > 5:
            self.recent_quotes.pop(0)

        return quote

    # ---------------- Other Handlers ----------------
    def handle_transactions(self):
        self.clear_content_frame()
        TransactionsWindow(self.content_frame, self.user_id, self.show_floating_message, self.show_error_message)

    def handle_debts(self):
        from debts_gui import DebtsWindow
        self.clear_content_frame()
        DebtsWindow(self.content_frame, self.user_id, self.show_floating_message, self.show_error_message)

    def handle_savings(self):
        from savings_manager_gui import SavingsWindow
        self.clear_content_frame()
        SavingsWindow(self.content_frame, self.user_id, self.show_floating_message, self.show_error_message)

    def handle_fd(self):
        from fixed_deposits_gui import FixedDepositsWindow
        self.clear_content_frame()
        FixedDepositsWindow(self.content_frame, self.user_id, self.show_floating_message, self.show_error_message)

    def handle_savings_graph(self):
        self.clear_content_frame()
        bg_color = self.root.cget("background")
        fg_color = "#ffffff" if "dark" in self.style.theme_use().lower() else "#000000"
        SavingsGraphWindow(
            self.content_frame,
            self.user_id,
            self.get_db_connection(),
            theme_bg=bg_color,
            theme_fg=fg_color
        )

    def show_themes_screen(self):
        self.clear_content_frame()

        canvas = tk.Canvas(self.content_frame, borderwidth=0, background="#222222")
        scroll_frame = ttk.Frame(canvas)
        scrollbar = ttk.Scrollbar(self.content_frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")

        scroll_frame.bind("<Configure>", lambda event: canvas.configure(scrollregion=canvas.bbox("all")))

        ttk.Label(scroll_frame, text="Select Theme", font=("Helvetica", 16, "bold")).pack(pady=10)

        for theme in self.style.theme_names():
            btn = ttk.Button(scroll_frame, text=theme.capitalize(), width=20,
                             command=lambda t=theme: self.apply_theme(t))
            btn.pack(pady=5)

    def apply_theme(self, theme_name):
        self.style.theme_use(theme_name)
        self.show_floating_message(f"Theme changed to {theme_name}")

    def show_credit_info(self):
        self.clear_content_frame()
        credit_frame = ttk.Frame(self.content_frame, padding=20)
        credit_frame.place(relx=0.5, rely=0.5, anchor="center")  # ✅ centered

        ttk.Label(credit_frame, text="Credits", font=("Helvetica", 16, "bold"), foreground="#00ffcc").pack(pady=10)
        ttk.Label(credit_frame, text="Team: Radeon 5090 Supercharged", font=("Helvetica", 12, "bold"), foreground="#00ffaa").pack(pady=5)

        members = [
            ("•  D. Hrithick", "Roll No: 23"),
            ("•  S. Lalith Akash", "Roll No: 24"),
            ("•  G. Ragav Krishna", "Roll No: 29")
        ]
        for name, roll in members:
            row = ttk.Frame(credit_frame)
            row.pack(anchor="w", pady=2)
            ttk.Label(row, text=name, width=20, anchor="w", font=("Helvetica", 12)).pack(side="left")
            ttk.Label(row, text=roll, font=("Helvetica", 12)).pack(side="left")

        ttk.Button(credit_frame, text="Back to Home", command=self.show_home_screen, bootstyle=SECONDARY).pack(pady=20)

    def get_db_connection(self):
        return mysql.connector.MySQLConnection(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name
        )

    def get_total_balance(self):
        conn = mysql.connector.MySQLConnection(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name
        )
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(amount) FROM transactions WHERE user_id = %s AND type = 'income'", (self.user_id,))
        income = cursor.fetchone()[0] or 0

        cursor.execute("SELECT SUM(amount) FROM transactions WHERE user_id = %s AND type = 'expense'", (self.user_id,))
        expenses = cursor.fetchone()[0] or 0
        cursor.close()
        conn.close()

        return income - expenses

    # ---------------- Floating Messages ----------------
    def show_floating_message(self, message_text, color="#00ffff"):
        label = tk.Label(self.root, text=message_text, font=("Helvetica", 14, "bold"), fg=color, bg=self.root.cget("background"))
        label.update_idletasks()

        x = (self.root.winfo_width() - label.winfo_width()) // 2
        y = self.root.winfo_height() - 40
        label.place(x=x, y=y)

        steps = 212
        fps_delay = 33

        def animate(step=0):
            if step > steps:
                label.destroy()
                return
            label.place_configure(y=y + step)
            fade_ratio = max(0, 1 - step / steps)
            try:
                r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
            except:
                r, g, b = 0, 255, 255
            r, g, b = int(r * fade_ratio), int(g * fade_ratio), int(b * fade_ratio)
            label.config(fg=f"#{r:02x}{g:02x}{b:02x}")
            self.root.after(fps_delay, animate, step + 1)

        animate()

    def show_error_message(self, message_text):
        label = tk.Label(self.root, text=message_text, font=("Helvetica", 10, "bold"), fg="#ff4444", bg="#2b2b00", padx=10, pady=4)
        label.update_idletasks()

        x = (self.root.winfo_width() - label.winfo_width()) // 2
        y = self.root.winfo_height() - 30
        label.place(x=x, y=y)

        steps = 212
        fps_delay = 33

        def animate(step=0):
            if step > steps:
                label.destroy()
                return
            label.place_configure(y=y + step)
            fade_ratio = max(0, 1 - step / steps)
            r, g, b = int(255 * fade_ratio), int(68 * fade_ratio), int(68 * fade_ratio)
            label.config(fg=f"#{r:02x}{g:02x}{b:02x}")
            self.root.after(fps_delay, animate, step + 1)

        animate()


if __name__ == "__main__":
    root = ttk.Window(themename="cyborg")
    root.geometry("900x600")
    app = FinanceManagerApp(root)
    root.mainloop()
