import mysql.connector
from datetime import date
from decimal import Decimal
from db_config import db_host, db_user, db_password, db_name


def calculate_monthly_savings(user_id):
    """
    Calculates and inserts monthly savings for the user only if not already recorded for this month.
    """

    today = date.today()
    first_of_month = today.replace(day=1)

    try:
        conn = mysql.connector.MySQLConnection(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name
        )
        cursor = conn.cursor()

        cursor.execute("""
            SELECT savings FROM monthly_savings
            WHERE user_id = %s AND month = %s
        """, (user_id, first_of_month))
        if cursor.fetchone():
            print(f"Monthly savings for {first_of_month.strftime('%B %Y')} already recorded.")
            return

        cursor.execute("SELECT monthly_salary FROM user_financial_summary WHERE user_id = %s", (user_id,))
        salary_result = cursor.fetchone()
        monthly_salary = salary_result[0] if salary_result else Decimal('0.00')

        cursor.execute("""
            SELECT SUM(amount) FROM transactions
            WHERE user_id = %s AND type = 'income'
            AND MONTH(date) = MONTH(%s) AND YEAR(date) = YEAR(%s)
        """, (user_id, today, today))
        income_result = cursor.fetchone()
        monthly_income = income_result[0] if income_result[0] else Decimal('0.00')

        cursor.execute("""
            SELECT SUM(amount) FROM transactions
            WHERE user_id = %s AND type = 'expense'
            AND MONTH(date) = MONTH(%s) AND YEAR(date) = YEAR(%s)
        """, (user_id, today, today))
        expense_result = cursor.fetchone()
        monthly_expense = expense_result[0] if expense_result[0] else Decimal('0.00')

        cursor.execute("SELECT SUM(monthly_payment) FROM debts WHERE user_id = %s", (user_id,))
        emi_result = cursor.fetchone()
        total_emi = emi_result[0] if emi_result[0] else Decimal('0.00')

        savings = monthly_salary + monthly_income - monthly_expense - total_emi

        cursor.execute("""
            INSERT INTO monthly_savings (user_id, month, savings)
            VALUES (%s, %s, %s)
        """, (user_id, first_of_month, savings))
        conn.commit()

        print(f"Monthly savings for {first_of_month.strftime('%B %Y')}: ₹{savings:.2f}")

    except Exception as e:
        print("Error calculating savings:", e)

    finally:
        cursor.close()
        conn.close()


def view_savings_history(user_id):
    """
    Displays the monthly savings history for a given user.
    """

    print("\n=== Monthly Savings History ===")

    try:
        conn = mysql.connector.MySQLConnection(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name
        )
        cursor = conn.cursor()

        cursor.execute("""
            SELECT month, savings FROM monthly_savings
            WHERE user_id = %s
            ORDER BY month ASC
        """, (user_id,))
        savings_records = cursor.fetchall()

        if not savings_records:
            print("No savings history found.")
            return

        for record in savings_records:
            month = record[0].strftime("%B %Y")
            amount = record[1]
            print(f"{month}: ₹{amount:.2f}")

    except Exception as e:
        print("Error retrieving savings history:", e)

    finally:
        cursor.close()
        conn.close()


def predict_retirement_savings(user_id):
    """
    Predicts total savings till retirement based on historical data.
    """

    try:
        conn = mysql.connector.MySQLConnection(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name
        )
        cursor = conn.cursor()

        cursor.execute("""
            SELECT age, retirement_age 
            FROM user_financial_summary 
            WHERE user_id = %s
        """, (user_id,))
        user_info = cursor.fetchone()
        if not user_info:
            print("User not found.")
            return

        current_age, retirement_age = user_info
        working_years_left = retirement_age - current_age
        if working_years_left <= 0:
            print("User already retired or retirement age not valid.")
            return

        cursor.execute("""
            SELECT 
                YEAR(date) AS year,
                MONTH(date) AS month,
                SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) AS total_income,
                SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) AS total_expense
            FROM transactions
            WHERE user_id = %s
            GROUP BY year, month
            ORDER BY year DESC, month DESC
            LIMIT 36
        """, (user_id,))
        monthly_data = cursor.fetchall()

        if not monthly_data:
            print("No transaction data available.")
            return

        total_savings = 0
        for row in monthly_data:
            year, month, income, expense = row
            monthly_saving = (income or 0) - (expense or 0)
            total_savings += monthly_saving

        months_considered = len(monthly_data)
        avg_monthly_saving = total_savings / months_considered

        months_left = working_years_left * 12
        predicted_total_savings = avg_monthly_saving * months_left

        print("\n=== Retirement Savings Prediction ===")
        print(f" Age: {current_age}, Retirement Age: {retirement_age}")
        print(f" Months of data analyzed: {months_considered}")
        print(f" Average Monthly Saving: ₹{avg_monthly_saving:.2f}")
        print(f"Predicted Savings till Retirement: ₹{predicted_total_savings:,.2f}")

    except Exception as e:
        print("Error predicting retirement savings:", e)

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()
