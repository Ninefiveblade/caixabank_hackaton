from datetime import datetime, timedelta, timezone
from http import HTTPStatus

import numpy as np
from dateutil.parser import parse
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app import db
from app.models import Transaction, User
from app.utils import check_alerts

transactions_bp = Blueprint("transactions", __name__)


def calculate_fraud(user_id, amount, category, timestamp):
    ninety_days_ago = timestamp - timedelta(days=90)
    transactions = Transaction.query.filter(
        Transaction.user_id == user_id, Transaction.timestamp >= ninety_days_ago
    ).all()
    if transactions:
        amounts = [t.amount for t in transactions]
        avg_spending = np.mean(amounts)
        std_dev = np.std(amounts)
        if amount > avg_spending + 3 * std_dev:
            return True
    six_months_ago = timestamp - timedelta(days=180)
    categories = (
        db.session.query(Transaction.category)
        .filter(Transaction.user_id == user_id, Transaction.timestamp >= six_months_ago)
        .distinct()
        .all()
    )
    categories = [c[0] for c in categories]
    if category not in categories:
        return True

    five_minutes_ago = timestamp - timedelta(minutes=5)
    recent_transactions = Transaction.query.filter(
        Transaction.user_id == user_id, Transaction.timestamp >= five_minutes_ago
    ).all()
    if len(recent_transactions) > 3:
        total_recent_amount = sum(t.amount for t in recent_transactions)
        daily_avg_spending = avg_spending if transactions else 0
        if total_recent_amount > daily_avg_spending:
            return True

    return False


@transactions_bp.route("/", methods=["POST"])
@jwt_required()
def add_transaction():
    user_id = get_jwt_identity()
    data = request.get_json()
    amount = data.get("amount")
    category = data.get("category")
    timestamp = data.get("timestamp", datetime.now(timezone.utc).isoformat())

    if not amount or not category:
        return jsonify({"msg": "No empty fields allowed."}), HTTPStatus.BAD_REQUEST

    timestamp = parse(timestamp)
    fraud = calculate_fraud(user_id, amount, category, timestamp)

    new_transaction = Transaction(
        user_id=user_id,
        amount=amount,
        category=category,
        timestamp=timestamp,
        fraud=fraud,
    )
    db.session.add(new_transaction)

    user = User.query.get(user_id)
    user.balance -= amount
    db.session.commit()

    check_alerts(user, new_transaction)

    return (
        jsonify(
            {
                "msg": "Transaction added and evaluated for fraud.",
                "data": {
                    "id": new_transaction.id,
                    "user_id": user_id,
                    "amount": amount,
                    "category": category,
                    "timestamp": timestamp.isoformat(),
                    "fraud": fraud,
                },
            }
        ),
        HTTPStatus.CREATED,
    )
