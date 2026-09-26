import tkinter as tk
from tkinter import ttk
from decimal import Decimal
from datetime import datetime, date
from fixed_deposits import load_fixed_deposits, add_fixed_deposit

class FixedDepositsWindow(ttk.Frame):
    def __init__(self, parent, user_id, show_floating_message_callback, show_error_message_callback):
        super().__init__(parent)
        self.user_id = user_id
        self.show_floating_message = show_floating_message_callback
        self.show_error_message = show_error_message_callback
        self.pack(fill="both", expand=True)

        self.create_widgets()
        self.refresh_fd_list()

    def create_widgets(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        self.view_tab = ttk.Frame(self.notebook)
        self.add_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.view_tab, text="View FDs")
        self.notebook.add(self.add_tab, text="Add FD")

        self.setup_view_tab()
        self.setup_add_tab()

    def setup_view_tab(self):
        self.tree = ttk.Treeview(
            self.view_tab, columns=("Amount", "Rate", "Start", "Maturity", "Option", "Return", "Closed"),
            show="headings"
        )
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.pack(fill="both", expand=True)

    def refresh_fd_list(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        fds = load_fixed_deposits(self.user_id)
        for fd in fds:
            self.tree.insert("", "end", values=(
                f"₹{fd['amount']}", f"{fd['interest_rate']}%",
                fd['start_date'], fd['maturity_date'],
                fd['payout_option'], f"₹{fd['expected_return']}",
                "Yes" if fd['is_closed'] else "No"
            ))

    def setup_add_tab(self):
        self.entries = {}

        # Amount
        ttk.Label(self.add_tab, text="Amount").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.entries["Amount"] = ttk.Entry(self.add_tab, width=30)
        self.entries["Amount"].grid(row=0, column=1, padx=5, pady=5)

        # Interest Rate
        ttk.Label(self.add_tab, text="Interest Rate").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.entries["Interest Rate"] = ttk.Entry(self.add_tab, width=30)
        self.entries["Interest Rate"].grid(row=1, column=1, padx=5, pady=5)

        # Start Date
        ttk.Label(self.add_tab, text="Start Date").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.start_day, self.start_month, self.start_year = self.create_date_dropdowns(self.add_tab, 2)

        # Maturity Date
        ttk.Label(self.add_tab, text="Maturity Date").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.maturity_day, self.maturity_month, self.maturity_year = self.create_date_dropdowns(self.add_tab, 3)

        # Payout Option dropdown
        ttk.Label(self.add_tab, text="Payout Option").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        self.payout_option = ttk.Combobox(self.add_tab, values=["monthly", "quarterly", "yearly", "maturity"], state="readonly", width=28)
        self.payout_option.set("maturity")
        self.payout_option.grid(row=4, column=1, padx=5, pady=5)

        # Note
        ttk.Label(self.add_tab, text="Note (optional)").grid(row=5, column=0, sticky="e", padx=5, pady=5)
        self.entries["Note"] = ttk.Entry(self.add_tab, width=30)
        self.entries["Note"].grid(row=5, column=1, padx=5, pady=5)

        # Add button
        add_button = ttk.Button(self.add_tab, text="Add Fixed Deposit", command=self.add_fd)
        add_button.grid(row=6, column=0, columnspan=2, pady=10)

    def create_date_dropdowns(self, parent, row):
        today = date.today()
        day_var = tk.StringVar(value=str(today.day))
        month_var = tk.StringVar(value=str(today.month))
        year_var = tk.StringVar(value=str(today.year))

        frame = ttk.Frame(parent)
        frame.grid(row=row, column=1, padx=5, pady=5, sticky="w")

        day_cb = ttk.Combobox(frame, textvariable=day_var, values=[f"{i:02}" for i in range(1, 32)], width=5, state="readonly")
        month_cb = ttk.Combobox(frame, textvariable=month_var, values=[f"{i:02}" for i in range(1, 13)], width=5, state="readonly")
        year_cb = ttk.Combobox(frame, textvariable=year_var, values=[str(i) for i in range(today.year, today.year + 31)], width=7, state="readonly")

        day_cb.pack(side="left", padx=2)
        month_cb.pack(side="left", padx=2)
        year_cb.pack(side="left", padx=2)

        return day_var, month_var, year_var

    def get_date_from_dropdowns(self, day, month, year):
        return date(int(year.get()), int(month.get()), int(day.get()))

    def add_fd(self):
        try:
            amount = Decimal(self.entries["Amount"].get().strip())
            interest_rate = Decimal(self.entries["Interest Rate"].get().strip())
            start_date = self.get_date_from_dropdowns(self.start_day, self.start_month, self.start_year)
            maturity_date = self.get_date_from_dropdowns(self.maturity_day, self.maturity_month, self.maturity_year)
            payout_option = self.payout_option.get().strip().lower()
            note = self.entries["Note"].get().strip()

            if payout_option not in ["monthly", "quarterly", "yearly", "maturity"]:
                self.show_error_message("Invalid payout option.")
                return

            add_fixed_deposit(self.user_id, amount, interest_rate, start_date, maturity_date, payout_option, note)
            self.refresh_fd_list()
            self.show_floating_message("Fixed Deposit added!", color="#00ff88")

            for entry in self.entries.values():
                entry.delete(0, tk.END)
            self.payout_option.set("maturity")

        except Exception as e:
            self.show_error_message(f"Error: {e}")
