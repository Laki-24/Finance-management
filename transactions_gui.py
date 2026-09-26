import tkinter as tk
from tkinter import ttk
from decimal import Decimal
import mysql.connector
from datetime import date, datetime
from calendar import monthrange
from db_config import db_host, db_user, db_password, db_name
from balance_updater import update_balance_on_transaction


class TransactionsWindow:
    def __init__(self, parent, user_id, show_floating_message_callback, show_error_message_callback):
        self.user_id = user_id
        self.show_floating_message = show_floating_message_callback
        self.show_error_message = show_error_message_callback

        self.frame = ttk.Frame(parent)
        self.frame.pack(fill="both", expand=True)

        ttk.Label(self.frame, text="Manage Transactions", font=("Helvetica", 16, "bold")).pack(pady=10)

        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.add_tab = ttk.Frame(self.notebook)
        self.view_tab = ttk.Frame(self.notebook)
        self.delete_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.add_tab, text="Add Transaction")
        self.notebook.add(self.view_tab, text="View Transactions")
        self.notebook.add(self.delete_tab, text="Delete Transaction")

        self.create_add_tab()
        self.create_view_tab()
        self.create_delete_tab()

    def create_add_tab(self):
        frame = self.add_tab
        form_frame = ttk.Frame(frame)
        form_frame.pack(pady=20)

        # Type
        ttk.Label(form_frame, text="Type:").grid(row=0, column=0, padx=5, pady=5)
        self.type_var = tk.StringVar()
        ttk.Combobox(form_frame, textvariable=self.type_var, values=["income", "expense"], state="readonly").grid(row=0, column=1)

        # Category
        ttk.Label(form_frame, text="Category:").grid(row=1, column=0, padx=5, pady=5)
        self.category_entry = ttk.Entry(form_frame)
        self.category_entry.grid(row=1, column=1)

        # Amount
        ttk.Label(form_frame, text="Amount:").grid(row=2, column=0, padx=5, pady=5)
        self.amount_entry = ttk.Entry(form_frame)
        self.amount_entry.grid(row=2, column=1)

        # Custom Date Picker (3 Comboboxes)
        ttk.Label(form_frame, text="Date:").grid(row=3, column=0, padx=5, pady=5)

        self.day_var = tk.StringVar()
        self.month_var = tk.StringVar()
        self.year_var = tk.StringVar()

        self.day_box = ttk.Combobox(form_frame, textvariable=self.day_var, state="readonly", width=5)
        self.month_box = ttk.Combobox(form_frame, textvariable=self.month_var, state="readonly", width=10,
                                      values=["January", "February", "March", "April", "May", "June",
                                              "July", "August", "September", "October", "November", "December"])
        self.year_box = ttk.Combobox(form_frame, textvariable=self.year_var, state="readonly", width=6,
                                     values=[str(y) for y in range(2000, 2101)])

        self.day_box.grid(row=3, column=1, sticky='w', padx=0)
        self.month_box.grid(row=3, column=1, padx=(45, 0))
        self.year_box.grid(row=3, column=1, sticky='e', padx=(0, 0))

        # Date logic bindings
        self.month_box.bind("<<ComboboxSelected>>", lambda e: self.update_days())
        self.year_box.bind("<<ComboboxSelected>>", lambda e: self.update_days())

        self.set_current_date()

        # Note
        ttk.Label(form_frame, text="Note:").grid(row=4, column=0, padx=5, pady=5)
        self.note_entry = ttk.Entry(form_frame)
        self.note_entry.grid(row=4, column=1)

        # Submit
        self.submit_btn = ttk.Button(form_frame, text="Add Transaction", command=self.add_transaction)
        self.submit_btn.grid(row=5, columnspan=2, pady=10)

    def update_days(self):
        try:
            year = int(self.year_var.get())
            month = self.month_box.current() + 1
            _, last_day = monthrange(year, month)
            days = [str(d) for d in range(1, last_day + 1)]
            current_day = self.day_var.get()

            self.day_box["values"] = days
            if current_day in days:
                self.day_var.set(current_day)
            else:
                self.day_var.set("1")
        except:
            pass

    def set_current_date(self):
        today = date.today()
        self.year_var.set(str(today.year))
        self.month_var.set(today.strftime("%B"))
        self.update_days()
        self.day_var.set(str(today.day))

    def get_selected_date(self):
        day = self.day_var.get()
        month = self.month_box.current() + 1
        year = self.year_var.get()
        return f"{year}-{month:02}-{int(day):02}"

    def create_view_tab(self):
        frame = self.view_tab

        container = ttk.Frame(frame)
        container.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(container, columns=("ID", "Type", "Category", "Amount", "Date", "Note"), show="headings")
        vsb = ttk.Scrollbar(container, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(container, orient="horizontal", command=self.tree.xview)

        self.tree.configure(yscroll=vsb.set, xscroll=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)

        refresh_btn = ttk.Button(frame, text="Refresh", command=self.load_transactions)
        refresh_btn.pack(pady=5)

        self.load_transactions()

    def create_delete_tab(self):
        frame = self.delete_tab
        form_frame = ttk.Frame(frame)
        form_frame.pack(pady=20)

        ttk.Label(form_frame, text="Enter Transaction ID to delete:").grid(row=0, column=0, padx=5, pady=5)
        self.delete_id_entry = ttk.Entry(form_frame)
        self.delete_id_entry.grid(row=0, column=1)

        delete_btn = ttk.Button(form_frame, text="Delete", command=self.delete_transaction)
        delete_btn.grid(row=1, columnspan=2, pady=10)

    def add_transaction(self):
        try:
            tx_type = self.type_var.get()
            category = self.category_entry.get()
            amount = Decimal(self.amount_entry.get())
            date = self.get_selected_date()
            note = self.note_entry.get()

            conn = mysql.connector.MySQLConnection(
                host=db_host, user=db_user, password=db_password, database=db_name
            )
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO transactions (user_id, type, category, amount, date, note)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (self.user_id, tx_type, category, amount, date, note))
            conn.commit()
            cursor.close()
            conn.close()

            update_balance_on_transaction(self.user_id, tx_type, amount)
            self.show_floating_message("Transaction added successfully!")
            self.clear_add_form()
            self.load_transactions()
        except Exception as e:
            self.show_error_message("Database Error: " + str(e))

    def delete_transaction(self):
        tid = self.delete_id_entry.get()
        if not tid.isdigit():
            self.show_error_message("Invalid transaction ID.")
            return

        try:
            conn = mysql.connector.MySQLConnection(
                host=db_host, user=db_user, password=db_password, database=db_name
            )
            cursor = conn.cursor()
            cursor.execute("DELETE FROM transactions WHERE user_id = %s AND transaction_id = %s", (self.user_id, tid))
            conn.commit()
            cursor.close()
            conn.close()
            self.show_floating_message("Transaction deleted successfully.")
            self.delete_id_entry.delete(0, tk.END)
            self.load_transactions()
        except Exception as e:
            self.show_error_message("Error deleting transaction: " + str(e))

    def load_transactions(self):
        try:
            conn = mysql.connector.MySQLConnection(
                host=db_host, user=db_user, password=db_password, database=db_name
            )
            cursor = conn.cursor()
            cursor.execute("""
                SELECT transaction_id, type, category, amount, date, note
                FROM transactions
                WHERE user_id = %s
            """, (self.user_id,))
            transactions = cursor.fetchall()
            cursor.close()
            conn.close()

            for row in self.tree.get_children():
                self.tree.delete(row)

            for txn in transactions:
                self.tree.insert("", tk.END, values=txn)

        except Exception as e:
            self.show_error_message("Failed to load transactions: " + str(e))

    def clear_add_form(self):
        self.type_var.set("")
        self.category_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)
        self.note_entry.delete(0, tk.END)
        self.set_current_date()


# Example usage
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Personal Finance Manager - Transactions")
    root.geometry("900x600")

    def dummy_msg(msg):
        print("✔️", msg)

    def dummy_err(msg):
        print("❌", msg)

    TransactionsWindow(root, user_id=1, show_floating_message_callback=dummy_msg, show_error_message_callback=dummy_err)
    root.mainloop()
