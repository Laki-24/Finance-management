import tkinter as tk
from tkinter import ttk
from ttkbootstrap import Frame, Label, Entry, Button
from ttkbootstrap.constants import *
import calendar
from datetime import datetime
from decimal import Decimal
import mysql.connector
from db_config import db_host, db_user, db_password, db_name


class DebtsWindow:
    def __init__(self, parent, user_id, show_floating_message_callback, show_error_message_callback):
        self.frame = Frame(parent)
        self.frame.pack(fill="both", expand=True)
        self.user_id = user_id
        self.show_floating_message = show_floating_message_callback
        self.show_error_message = show_error_message_callback

        Label(self.frame, text="Manage Debts", font=("Helvetica", 16, "bold")).pack(pady=10)

        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.add_tab = Frame(self.notebook)
        self.view_tab = Frame(self.notebook)
        self.modify_tab = Frame(self.notebook)

        self.notebook.add(self.add_tab, text="Add Debt")
        self.notebook.add(self.view_tab, text="View Debts")
        self.notebook.add(self.modify_tab, text="Modify Debt")

        self.create_add_tab()
        self.create_view_tab()
        self.create_modify_tab()

    def create_add_tab(self):
        frame = self.add_tab

        ttk.Label(frame, text="Debt Type").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.debt_type_entry = Entry(frame)
        self.debt_type_entry.grid(row=0, column=1, sticky="ew", padx=10, pady=5)

        ttk.Label(frame, text="Total Amount").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.amount_entry = Entry(frame)
        self.amount_entry.grid(row=1, column=1, sticky="ew", padx=10, pady=5)

        ttk.Label(frame, text="Interest Rate (optional)").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.interest_entry = Entry(frame)
        self.interest_entry.grid(row=2, column=1, sticky="ew", padx=10, pady=5)

        ttk.Label(frame, text="Monthly Payment").grid(row=3, column=0, sticky="w", padx=10, pady=5)
        self.payment_entry = Entry(frame)
        self.payment_entry.grid(row=3, column=1, sticky="ew", padx=10, pady=5)

        ttk.Label(frame, text="Start Date").grid(row=4, column=0, sticky="w", padx=10, pady=5)
        self.start_day, self.start_month, self.start_year = self.create_date_dropdowns(frame, 4, default_today=True)

        ttk.Label(frame, text="End Date (optional)").grid(row=5, column=0, sticky="w", padx=10, pady=5)
        self.end_day, self.end_month, self.end_year = self.create_date_dropdowns(frame, 5)

        Button(frame, text="Add Debt", command=self.add_debt).grid(row=6, column=0, columnspan=2, pady=20)

        frame.columnconfigure(1, weight=1)

    def create_date_dropdowns(self, parent, row, default_today=False):
        today = datetime.today()
        default_day = today.day if default_today else 1
        default_month = today.month if default_today else 1
        default_year = today.year if default_today else 2025

        date_frame = Frame(parent)
        date_frame.grid(row=row, column=1, sticky="w", padx=10, pady=5)

        day_var = tk.StringVar()
        month_var = tk.StringVar()
        year_var = tk.StringVar()

        def update_days(*args):
            try:
                m = int(month_var.get())
                y = int(year_var.get())
                if not (1 <= m <= 12): return
                days_in_month = calendar.monthrange(y, m)[1]
                current = day_var.get()
                day_cb['values'] = list(range(1, days_in_month + 1))
                day_var.set(current if current.isdigit() and 1 <= int(current) <= days_in_month else "1")
            except Exception:
                pass

        day_cb = ttk.Combobox(date_frame, textvariable=day_var, width=4)
        day_cb.grid(row=0, column=0)
        month_cb = ttk.Combobox(date_frame, textvariable=month_var, values=list(range(1, 13)), width=5)
        month_cb.grid(row=0, column=1, padx=5)
        year_cb = ttk.Combobox(date_frame, textvariable=year_var, values=list(range(2000, 2101)), width=7)
        year_cb.grid(row=0, column=2)

        month_cb.set(default_month)
        year_cb.set(default_year)
        update_days()
        day_cb.set(default_day)

        month_cb.bind("<<ComboboxSelected>>", update_days)
        year_cb.bind("<<ComboboxSelected>>", update_days)

        return day_var, month_var, year_var

    def add_debt(self):
        try:
            debt_type = self.debt_type_entry.get()
            amount = Decimal(self.amount_entry.get())
            interest_raw = self.interest_entry.get()
            interest = Decimal(interest_raw) if interest_raw else None
            monthly = Decimal(self.payment_entry.get())

            start_date = f"{self.start_year.get()}-{int(self.start_month.get()):02d}-{int(self.start_day.get()):02d}"
            try:
                end_date = f"{self.end_year.get()}-{int(self.end_month.get()):02d}-{int(self.end_day.get()):02d}"
            except:
                end_date = None

            conn = mysql.connector.connect(
                host=db_host, user=db_user, password=db_password, database=db_name
            )
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO debts (user_id, debt_type, total_amount, interest_rate, monthly_payment, start_date, end_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (self.user_id, debt_type, amount, interest, monthly, start_date, end_date))
            conn.commit()
            cur.close()
            conn.close()

            self.show_floating_message("Debt added successfully!", color="#00ff88")
            self.load_debts()

        except Exception as e:
            self.show_error_message(f"Error adding debt: {e}")

    def create_view_tab(self):
        frame = self.view_tab

        # Scrollbars
        y_scroll = ttk.Scrollbar(frame, orient="vertical")
        x_scroll = ttk.Scrollbar(frame, orient="horizontal")

        cols = ("ID", "Type", "Total", "Interest", "Monthly", "Start", "End")
        self.tree = ttk.Treeview(frame, columns=cols, show="headings",
                                 yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)

        y_scroll.config(command=self.tree.yview)
        x_scroll.config(command=self.tree.xview)

        self.tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")

        refresh_btn = Button(frame, text="Refresh", command=self.load_debts)
        refresh_btn.grid(row=2, column=0, pady=8)

        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        self.load_debts()

    def load_debts(self):
        try:
            conn = mysql.connector.connect(
                host=db_host, user=db_user, password=db_password, database=db_name
            )
            cur = conn.cursor()
            cur.execute("""
                SELECT debt_id, debt_type, total_amount, interest_rate,
                       monthly_payment, start_date, end_date
                FROM debts WHERE user_id = %s
            """, (self.user_id,))
            rows = cur.fetchall()
            cur.close()
            conn.close()

            for i in self.tree.get_children():
                self.tree.delete(i)
            for row in rows:
                self.tree.insert("", tk.END, values=row)

        except Exception as e:
            self.show_error_message(f"DB Load Error: {e}")

    def create_modify_tab(self):
        frame = self.modify_tab

        ttk.Label(frame, text="Debt ID to Modify:").grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.mod_id = Entry(frame)
        self.mod_id.grid(row=0, column=1, sticky="ew", padx=10)

        ttk.Label(frame, text="Field to Modify:").grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.mod_field = ttk.Combobox(frame, values=[
            "debt_type", "total_amount", "interest_rate", "monthly_payment", "start_date", "end_date"
        ])
        self.mod_field.grid(row=1, column=1, padx=10, sticky="ew")

        ttk.Label(frame, text="New Value:").grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.mod_value = Entry(frame)
        self.mod_value.grid(row=2, column=1, padx=10, sticky="ew")

        Button(frame, text="Update Debt", command=self.modify_debt).grid(row=3, column=0, columnspan=2, pady=15)

        frame.columnconfigure(1, weight=1)

    def modify_debt(self):
        try:
            debt_id = int(self.mod_id.get())
            field = self.mod_field.get().strip()
            new_val = self.mod_value.get().strip()

            if field in ("total_amount", "interest_rate", "monthly_payment") and new_val:
                new_val = Decimal(new_val)
            elif field in ("end_date", "interest_rate") and not new_val:
                new_val = None

            conn = mysql.connector.connect(
                host=db_host, user=db_user, password=db_password, database=db_name
            )
            cur = conn.cursor()
            cur.execute(f"UPDATE debts SET {field} = %s WHERE debt_id = %s AND user_id = %s", (new_val, debt_id, self.user_id))
            conn.commit()
            cur.close()
            conn.close()

            self.show_floating_message(f"{field} updated successfully!", color="#00ff88")
            self.mod_id.delete(0, tk.END)
            self.mod_value.delete(0, tk.END)
            self.load_debts()

        except Exception as e:
            self.show_error_message(f"Update Error: {e}")


# Callbacks for testing
def show_message(msg, color="green"):
    print(f"✔ {msg}")

def show_error(msg):
    print(f"✖ {msg}")


# --- Run if script is main ---
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Debt Manager")
    root.geometry("1000x700")
    root.minsize(800, 500)

    DebtsWindow(root, user_id=1, show_floating_message_callback=show_message, show_error_message_callback=show_error)
    root.mainloop()
