from http import HTTPStatus

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.utils import get_exchange_fee, get_exchange_rate

transfers_bp = Blueprint("transfers", __name__)


@transfers_bp.route("simulate", methods=["POST"])
@jwt_required()
def simulate_transfer():
    data = request.get_json()
    amount = data.get("amount")
    if amount <= 0:
        return (
            jsonify({"msg": "Amount must be greater than 0."}),
            HTTPStatus.BAD_REQUEST,
        )
    source_currency = data.get("source_currency")
    target_currency = data.get("target_currency")

    if not amount or not source_currency or not target_currency:
        return jsonify({"msg": "No empty fields allowed."}), HTTPStatus.BAD_REQUEST

    rate = get_exchange_rate(source_currency, target_currency)
    fee = get_exchange_fee(source_currency, target_currency)

    if rate is None or fee is None:
        return (
            jsonify({"msg": "Invalid currencies or no exchange data available."}),
            HTTPStatus.NOT_FOUND,
        )

    total_amount = amount * (1 - fee) * rate
    return (
        jsonify({"msg": f"Amount in target currency: {total_amount}."}),
        HTTPStatus.CREATED,
    )


@transfers_bp.route("fees", methods=["GET"])
@jwt_required()
def get_fees():
    source_currency = request.args.get("source_currency")
    target_currency = request.args.get("target_currency")

    if not source_currency or not target_currency:
        return jsonify({"msg": "No empty fields allowed."}), HTTPStatus.BAD_REQUEST

    fee = get_exchange_fee(source_currency, target_currency)
    if fee is None:
        return (
            jsonify({"msg": "No fee information available for these currencies."}),
            HTTPStatus.NOT_FOUND,
        )

    return jsonify({"fee": fee}), HTTPStatus.OK


@transfers_bp.route("rates", methods=["GET"])
@jwt_required()
def get_rates():
    currency_from = request.args.get("source_currency")
    currency_to = request.args.get("target_currency")

    if not currency_from or not currency_to:
        return jsonify({"msg": "No empty fields allowed."}), HTTPStatus.BAD_REQUEST

    rate = get_exchange_rate(currency_from, currency_to)
    if rate is None:
        return (
            jsonify({"msg": "No exchange rate available for these currencies."}),
            HTTPStatus.NOT_FOUND,
        )

    return jsonify({"rate": rate}), HTTPStatus.OK
