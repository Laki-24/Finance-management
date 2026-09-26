import mysql.connector
from datetime import date
import tkinter as tk
from tkinter import ttk
from db_config import db_host, db_user, db_password, db_name


class SavingsWindow:
    def __init__(self, parent, user_id, show_floating_message_callback, show_error_message_callback):
        self.user_id = user_id
        self.show_floating_message = show_floating_message_callback
        self.show_error_message = show_error_message_callback

        self.frame = ttk.Frame(parent)
        self.frame.pack(fill="both", expand=True)

        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.history_tab = ttk.Frame(self.notebook)
        self.predict_tab = ttk.Frame(self.notebook)
        self.update_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.history_tab, text="View Savings History")
        self.notebook.add(self.predict_tab, text="Predict Retirement Savings")
        self.notebook.add(self.update_tab, text="Update Retirement Age")

        self.create_history_tab()
        self.create_prediction_tab()
        self.create_update_tab()

    def create_history_tab(self):
        frame = self.history_tab

        self.tree = ttk.Treeview(frame, columns=("Month", "Savings"), show="headings", height=15)
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        self.tree.heading("Month", text="Month")
        self.tree.heading("Savings", text="Saved Amount (₹)")
        self.tree.column("Month", width=150)
        self.tree.column("Savings", width=150)

        refresh_btn = ttk.Button(frame, text="Refresh", command=self.display_savings_history)
        refresh_btn.pack(pady=5)

        self.display_savings_history()

    def create_prediction_tab(self):
        frame = self.predict_tab
        form_frame = ttk.Frame(frame)
        form_frame.pack(pady=30)

        ttk.Label(form_frame, text="Enter Your Current Age:").grid(row=0, column=0, padx=10, pady=10)
        self.age_entry = ttk.Entry(form_frame)
        self.age_entry.grid(row=0, column=1, padx=10, pady=10)

        predict_btn = ttk.Button(form_frame, text="Predict", command=self.display_retirement_prediction)
        predict_btn.grid(row=0, column=2, padx=10)

        self.prediction_label = ttk.Label(frame, text="", wraplength=600, justify="center", font=("Segoe UI", 11))
        self.prediction_label.pack(pady=20)

    def create_update_tab(self):
        frame = self.update_tab
        form_frame = ttk.Frame(frame)
        form_frame.pack(pady=30)

        ttk.Label(form_frame, text="Enter New Retirement Age (40–80):").grid(row=0, column=0, padx=10, pady=10)
        self.retirement_age_entry = ttk.Entry(form_frame)
        self.retirement_age_entry.grid(row=0, column=1, padx=10, pady=10)

        update_btn = ttk.Button(form_frame, text="Update", command=self.update_retirement_age)
        update_btn.grid(row=0, column=2, padx=10)

    def display_savings_history(self):
        try:
            conn = mysql.connector.MySQLConnection(
                host=db_host, user=db_user, password=db_password, database=db_name
            )
            cursor = conn.cursor()
            cursor.execute("""
                SELECT month, savings FROM monthly_savings
                WHERE user_id = %s ORDER BY month ASC
            """, (self.user_id,))
            savings_records = cursor.fetchall()

            for row in self.tree.get_children():
                self.tree.delete(row)

            if not savings_records:
                self.show_floating_message("No savings history found.")
                return

            for record in savings_records:
                month = record[0].strftime("%B %Y")
                amount = f"₹{record[1]:,.2f}"
                self.tree.insert("", "end", values=(month, amount))

        except Exception as e:
            self.show_error_message("Error loading savings history.")
            print(e)
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def display_retirement_prediction(self):
        try:
            current_age_input = self.age_entry.get().strip()
            if not current_age_input or not current_age_input.isdigit():
                self.show_error_message("Please enter a valid current age.")
                return

            current_age = int(current_age_input)

            conn = mysql.connector.MySQLConnection(
                host=db_host, user=db_user, password=db_password, database=db_name
            )
            cursor = conn.cursor()

            cursor.execute("SELECT retirement_age FROM user_financial_summary WHERE user_id = %s", (self.user_id,))
            result = cursor.fetchone()

            if not result:
                self.show_error_message("User data not found.")
                return

            retirement_age = result[0] or 60
            years_left = retirement_age - current_age

            if years_left <= 0:
                self.show_error_message("Already retired or invalid input.")
                return

            cursor.execute("""
                SELECT 
                    YEAR(date), MONTH(date),
                    SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END),
                    SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END)
                FROM transactions
                WHERE user_id = %s
                GROUP BY YEAR(date), MONTH(date)
                ORDER BY YEAR(date) DESC, MONTH(date) DESC
                LIMIT 36
            """, (self.user_id,))
            monthly_data = cursor.fetchall()

            if not monthly_data:
                self.show_error_message("No transaction data.")
                return

            total_savings = sum((income or 0) - (expense or 0) for _, _, income, expense in monthly_data)
            months = len(monthly_data)

            avg_monthly_saving = total_savings / months
            predicted_savings = avg_monthly_saving * (years_left * 12)

            self.prediction_label.config(
                text=f"Predicted savings by age {retirement_age}: ₹{predicted_savings:,.2f}"
            )
            self.show_floating_message("Prediction updated.")

        except Exception as e:
            self.show_error_message("Prediction error.")
            import traceback
            traceback.print_exc()
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    def update_retirement_age(self):
        try:
            new_age_input = self.retirement_age_entry.get().strip()
            if not new_age_input or not new_age_input.isdigit():
                self.show_error_message("Enter a valid age.")
                return

            new_age = int(new_age_input)
            if new_age < 40 or new_age > 80:
                self.show_error_message("Age must be between 40 and 80.")
                return

            conn = mysql.connector.MySQLConnection(
                host=db_host, user=db_user, password=db_password, database=db_name
            )
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE user_financial_summary
                SET retirement_age = %s
                WHERE user_id = %s
            """, (new_age, self.user_id))
            conn.commit()

            self.show_floating_message(f"Retirement age updated to {new_age}.")

        except Exception as e:
            self.show_error_message("Error updating age.")
            print(e)
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()
