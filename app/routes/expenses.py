from datetime import datetime, timedelta
from http import HTTPStatus

from dateutil.relativedelta import relativedelta
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app import db
from app.models import RecurringExpense

expenses_bp = Blueprint("expenses", __name__)


@expenses_bp.route("/", methods=["POST"])
@jwt_required()
def create_expense():
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data:
        return jsonify({"msg": "No data provided."}), HTTPStatus.BAD_REQUEST

    required_fields = ["expense_name", "amount", "frequency", "start_date"]
    if not all(field in data for field in required_fields):
        return jsonify({"msg": "No empty fields allowed."}), HTTPStatus.BAD_REQUEST

    try:
        start_date = datetime.strptime(data["start_date"], "%Y-%m-%d")
    except ValueError:
        return (
            jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}),
            HTTPStatus.BAD_REQUEST,
        )

    if data["frequency"] not in ["daily", "weekly", "monthly"]:
        return (
            jsonify({"error": "Frequency must be 'daily', 'weekly', or 'monthly'."}),
            HTTPStatus.BAD_REQUEST,
        )

    if data["amount"] <= 0:
        return (
            jsonify({"error": "Amount must be greater than 0."}),
            HTTPStatus.BAD_REQUEST,
        )

    expense = RecurringExpense(
        user_id=user_id,
        expense_name=data["expense_name"],
        amount=data["amount"],
        frequency=data["frequency"],
        start_date=start_date,
    )
    db.session.add(expense)
    db.session.commit()

    return (
        jsonify(
            {
                "msg": "Recurring expense added successfully.",
                "data": {
                    "id": expense.id,
                    "expense_name": expense.expense_name,
                    "amount": expense.amount,
                    "frequency": expense.frequency,
                    "start_date": expense.start_date.strftime("%Y-%m-%d"),
                },
            }
        ),
        HTTPStatus.CREATED,
    )


@expenses_bp.route("/", methods=["GET"])
@jwt_required()
def get_expenses():
    user_id = get_jwt_identity()
    expenses = RecurringExpense.query.filter_by(user_id=user_id).all()
    return (
        jsonify(
            [
                {
                    "id": expense.id,
                    "expense_name": expense.expense_name,
                    "amount": expense.amount,
                    "frequency": expense.frequency,
                    "start_date": expense.start_date.strftime("%Y-%m-%d"),
                }
                for expense in expenses
            ]
        ),
        HTTPStatus.OK,
    )


@expenses_bp.route("/<int:expense_id>", methods=["DELETE"])
@jwt_required()
def delete_expense(expense_id):
    user_id = get_jwt_identity()
    expense = RecurringExpense.query.filter_by(id=expense_id, user_id=user_id).first()

    if not expense:
        return jsonify({"error": "Expense not found."}), HTTPStatus.NOT_FOUND

    db.session.delete(expense)
    db.session.commit()

    return jsonify({"message": "Expense deleted successfully."}), HTTPStatus.OK


@expenses_bp.route("/<int:expense_id>", methods=["PUT"])
@jwt_required()
def update_expense(expense_id):
    user_id = get_jwt_identity()
    data = request.get_json()

    if not data:
        return jsonify({"msg": "No data provided."}), HTTPStatus.BAD_REQUEST

    expense = RecurringExpense.query.filter_by(id=expense_id, user_id=user_id).first()
    if not expense:
        return jsonify({"msg": "Expense not found."}), HTTPStatus.NOT_FOUND

    if "expense_name" in data:
        expense.expense_name = data["expense_name"]
    if "amount" in data:
        if data["amount"] <= 0:
            return (
                jsonify({"msg": "Amount must be greater than 0."}),
                HTTPStatus.BAD_REQUEST,
            )
        expense.amount = data["amount"]
    if "frequency" in data:
        if data["frequency"] not in ["daily", "weekly", "monthly"]:
            return jsonify({"msg": "Invalid frequency."}), HTTPStatus.BAD_REQUEST
        expense.frequency = data["frequency"]
    if "start_date" in data:
        try:
            expense.start_date = datetime.strptime(data["start_date"], "%Y-%m-%d")
        except ValueError:
            return (
                jsonify({"msg": "Invalid date format. Use YYYY-MM-DD."}),
                HTTPStatus.BAD_REQUEST,
            )

    db.session.commit()

    return (
        jsonify(
            {
                "msg": "Recurring expense updated successfully.",
                "data": {
                    "id": expense.id,
                    "expense_name": expense.expense_name,
                    "amount": expense.amount,
                    "frequency": expense.frequency,
                    "start_date": expense.start_date.strftime("%Y-%m-%d"),
                },
            }
        ),
        HTTPStatus.OK,
    )


@expenses_bp.route("/projection", methods=["GET"])
@jwt_required()
def get_projection():
    user_id = get_jwt_identity()
    expenses = RecurringExpense.query.filter_by(user_id=user_id).all()
    projection = {}
    for expense in expenses:
        projection[expense.id] = []
        date = expense.start_date
        for _ in range(30):
            projection[expense.id].append(date.strftime("%Y-%m-%d"))
            if expense.frequency == "daily":
                date += timedelta(days=1)
            elif expense.frequency == "weekly":
                date += timedelta(weeks=1)
            elif expense.frequency == "monthly":
                date += relativedelta(months=1)
    return jsonify(projection), HTTPStatus.OK
