import mysql.connector
from datetime import date, datetime
from decimal import Decimal
from db_config import db_host, db_user, db_password, db_name  # Import credentials

# Message function placeholder (set by GUI)
show_message_func = None

def msg(text, color="black"):
    if show_message_func:
        show_message_func(text, color)
    else:
        print(text)

def update_balance_on_transaction(user_id, transaction_type, amount):
    """
    Updates the total_balance in user_financial_summary table based on the new transaction.
    Income increases balance, expense decreases it.
    """
    amount = Decimal(str(amount))
    conn = mysql.connector.MySQLConnection(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )
    cursor = conn.cursor()

    # Get current balance
    cursor.execute("SELECT total_balance FROM user_financial_summary WHERE user_id = %s", (user_id,))
    result = cursor.fetchone()

    if result is None:
        msg("User financial summary not found.", "red")
        cursor.close()
        conn.close()
        return

    current_balance = result[0]

    # Update based on transaction type
    if transaction_type == 'income':
        new_balance = current_balance + amount
    elif transaction_type == 'expense':
        new_balance = current_balance - amount
    else:
        msg("Invalid transaction type.", "red")
        cursor.close()
        conn.close()
        return

    # Update balance and last_updated
    cursor.execute("""
        UPDATE user_financial_summary
        SET total_balance = %s, last_updated = %s
        WHERE user_id = %s
    """, (new_balance, date.today(), user_id))

    conn.commit()
    cursor.close()
    conn.close()
    msg("Balance updated after transaction.", "green")

def apply_monthly_update(user_id):
    """
    Adds monthly salary and subtracts total EMI using the transactions table and balance updater.
    Should be called at the start of each month.
    """
    try:
        conn = mysql.connector.MySQLConnection(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name
        )
        cursor = conn.cursor()

        # Fetch user salary, current balance and last update date
        cursor.execute("""
            SELECT monthly_salary, total_balance, last_updated 
            FROM user_financial_summary 
            WHERE user_id = %s
        """, (user_id,))
        result = cursor.fetchone()

        if not result:
            msg("User financial summary not found.", "red")
            return

        monthly_salary, total_balance, last_updated = result
        today = date.today()

        if last_updated and last_updated.month == today.month and last_updated.year == today.year:
            msg("Monthly update already applied.", "blue")
            return

        # Fetch total EMI
        cursor.execute("SELECT SUM(monthly_payment) FROM debts WHERE user_id = %s", (user_id,))
        emi_result = cursor.fetchone()
        total_emi = emi_result[0] if emi_result[0] else 0

        # Add salary
        if monthly_salary > 0:
            cursor.execute("""
                INSERT INTO transactions (user_id, type, category, amount, date, note)
                VALUES (%s, 'income', 'Salary', %s, CURDATE(), 'Monthly salary credited')
            """, (user_id, monthly_salary))
            update_balance_on_transaction(user_id, 'income', monthly_salary)

        # Deduct EMI
        if total_emi > 0:
            cursor.execute("""
                INSERT INTO transactions (user_id, type, category, amount, date, note)
                VALUES (%s, 'expense', 'EMI', %s, CURDATE(), 'Monthly EMI deduction')
            """, (user_id, total_emi))
            update_balance_on_transaction(user_id, 'expense', total_emi)

        # Update last_updated
        cursor.execute("""
            UPDATE user_financial_summary 
            SET last_updated = %s 
            WHERE user_id = %s
        """, (today, user_id))

        conn.commit()
        msg(f"Monthly update applied. Salary: ₹{monthly_salary}, EMI: ₹{total_emi}.", "green")

    except Exception as e:
        msg(f"Error in monthly update: {e}", "red")

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals() and conn.is_connected():
            conn.close()
