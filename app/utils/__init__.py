"""
This module contains utility functions for the application.
"""

from pathlib import Path

import pandas as pd
from email_validator import EmailNotValidError, validate_email

from app.models import Alert
from app.services import MESSAGE_BALANCE_DROP, MESSAGE_SAVING, send_email

path = Path(__file__).parent.parent

exchange_rates = pd.read_csv(path / "exchange_rates.csv")
exchange_fees = pd.read_csv(path / "exchange_fees.csv")


def get_exchange_rate(source_currency, target_currency):
    rate = exchange_rates[
        (exchange_rates["currency_from"] == source_currency)
        & (exchange_rates["currency_to"] == target_currency)
    ]
    if rate.empty:
        return None
    return rate.iloc[0]["rate"]


def get_exchange_fee(source_currency, target_currency):
    fee = exchange_fees[
        (exchange_fees["currency_from"] == source_currency)
        & (exchange_fees["currency_to"] == target_currency)
    ]
    if fee.empty:
        return None
    return fee.iloc[0]["fee"]


def check_alerts(user, transaction):
    alerts = Alert.query.filter_by(user_id=user.id).all()
    for alert in alerts:
        if alert.target_amount and user.balance >= alert.target_amount:
            body = MESSAGE_SAVING.format(
                user_name=user.name, alert_target_amount=alert.target_amount
            )
            send_email("Savings Alert", user.email, body)
        if (
            alert.balance_drop_threshold
            and user.balance <= alert.balance_drop_threshold
        ):
            body = MESSAGE_BALANCE_DROP.format(
                user_name=user.name,
                alert_balance_drop_threshold=alert.balance_drop_threshold,
            )
            send_email("Balance Drop Alert", user.email, body)


def check_email(email: str) -> bool:
    try:
        validate_email(email, check_deliverability=True)
        return True
    except EmailNotValidError:
        return False
