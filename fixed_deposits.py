import mysql.connector
from datetime import datetime, timedelta, date
from decimal import Decimal
from db_config import db_host, db_user, db_password, db_name

def add_fixed_deposit(user_id, amount, interest_rate, start_date, maturity_date, payout_option, note=""):
    """
    Adds a new fixed deposit record for the user.
    Calculates expected return using simple interest.
    """
    days = (maturity_date - start_date).days
    years = days / 365
    expected_return = Decimal(amount) * (Decimal(interest_rate) / 100) * Decimal(years)

    conn = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO fixed_deposits 
        (user_id, amount, interest_rate, start_date, maturity_date, payout_option, expected_return, is_closed, note)
        VALUES (%s, %s, %s, %s, %s, %s, %s, 0, %s)
    """, (user_id, amount, interest_rate, start_date, maturity_date, payout_option, expected_return, note))
    conn.commit()
    cursor.close()
    conn.close()

def load_fixed_deposits(user_id):
    """
    Returns a list of fixed deposits for the given user_id.
    Each item is a dict with keys matching table columns.
    """
    conn = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT * FROM fixed_deposits WHERE user_id = %s
    """, (user_id,))
    fds = cursor.fetchall()
    cursor.close()
    conn.close()
    return fds

def update_fd_interest_if_due(user_id):
    """
    Checks all open fixed deposits for the user.
    Updates balance in `user_financial_summary`, not in `users` table.
    """
    conn = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )
    cursor = conn.cursor(dictionary=True)

    # Fetch user balance from user_financial_summary
    cursor.execute("SELECT total_balance FROM user_financial_summary WHERE user_id = %s", (user_id,))
    user_balance_row = cursor.fetchone()
    if not user_balance_row:
        cursor.close()
        conn.close()
        return  # User not found

    balance = Decimal(user_balance_row['total_balance'])

    # Get all open FDs for user
    cursor.execute("""
        SELECT * FROM fixed_deposits WHERE user_id = %s AND is_closed = 0
    """, (user_id,))
    fds = cursor.fetchall()

    updated = False
    today = date.today()

    for fd in fds:
        amount = Decimal(fd['amount'])
        rate = Decimal(fd['interest_rate'])
        start_date = fd['start_date']
        maturity_date = fd['maturity_date']
        payout_option = fd['payout_option']
        expected_return = Decimal(fd['expected_return'])
        fd_id = fd['fd_id']

        if payout_option == 'maturity':
            if today >= maturity_date:
                maturity_amount = amount + expected_return
                balance += maturity_amount

                cursor.execute("""
                    UPDATE fixed_deposits SET is_closed = 1 WHERE fd_id = %s
                """, (fd_id,))
                updated = True

        else:
            delta_days = (today - start_date).days
            if payout_option == 'monthly':
                payout_period_days = 30
            elif payout_option == 'quarterly':
                payout_period_days = 90
            elif payout_option == 'yearly':
                payout_period_days = 365
            else:
                continue

            total_payouts_due = delta_days // payout_period_days

            total_days = (maturity_date - start_date).days
            total_years = Decimal(total_days) / Decimal(365)
            total_interest = amount * (rate / 100) * total_years

            interest_per_payout = total_interest / Decimal(total_payouts_due if total_payouts_due else 1)

            payouts_done = int((expected_return / interest_per_payout).to_integral_value(rounding='ROUND_FLOOR')) if expected_return > 0 else 0
            payouts_to_pay = total_payouts_due - payouts_done

            if payouts_to_pay > 0:
                interest_to_add = interest_per_payout * Decimal(payouts_to_pay)
                balance += interest_to_add

                new_expected_return = expected_return + interest_to_add
                cursor.execute("""
                    UPDATE fixed_deposits SET expected_return = %s WHERE fd_id = %s
                """, (new_expected_return, fd_id))
                updated = True

            if today >= maturity_date:
                cursor.execute("""
                    UPDATE fixed_deposits SET is_closed = 1 WHERE fd_id = %s
                """, (fd_id,))
                updated = True

    if updated:        
        cursor.execute("""
            UPDATE user_financial_summary SET total_balance = %s WHERE user_id = %s
        """, (balance, user_id))

    conn.commit()
    cursor.close()
    conn.close()

def close_fd(fd_id):
    """
    Manually close a fixed deposit by fd_id.
    """
    conn = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE fixed_deposits SET is_closed = 1 WHERE fd_id = %s
    """, (fd_id,))
    conn.commit()
    cursor.close()
    conn.close()
