from datetime import datetime, timezone
from http import HTTPStatus

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app import db
from app.models import Alert

alerts_bp = Blueprint("alerts", __name__)


@alerts_bp.route("amount_reached", methods=["POST"])
@jwt_required()
def create_amount_reached_alert():
    user_id = get_jwt_identity()
    data = request.get_json()
    target_amount = data.get("target_amount")
    alert_threshold = data.get("alert_threshold")

    if not target_amount or not alert_threshold:
        return jsonify({"msg": "No empty fields allowed."}), HTTPStatus.BAD_REQUEST

    new_alert = Alert(
        user_id=user_id,
        target_amount=target_amount,
        alert_threshold=alert_threshold,
        created_at=datetime.now(timezone.utc),
    )
    db.session.add(new_alert)
    db.session.commit()

    return (
        jsonify(
            {
                "msg": "Correctly added savings alert!",
                "data": {
                    "id": new_alert.id,
                    "user_id": user_id,
                    "target_amount": target_amount,
                    "alert_threshold": alert_threshold,
                },
            }
        ),
        HTTPStatus.CREATED,
    )


@alerts_bp.route("balance_drop", methods=["POST"])
@jwt_required()
def create_balance_drop_alert():
    user_id = get_jwt_identity()
    data = request.get_json()
    balance_drop_threshold = data.get("balance_drop_threshold")

    if not balance_drop_threshold:
        return jsonify({"msg": "No empty fields allowed."}), HTTPStatus.BAD_REQUEST

    new_alert = Alert(
        user_id=user_id,
        balance_drop_threshold=balance_drop_threshold,
        created_at=datetime.utcnow(),
    )
    db.session.add(new_alert)
    db.session.commit()

    return (
        jsonify(
            {
                "msg": "Correctly added balance drop alert!",
                "data": {
                    "id": new_alert.id,
                    "user_id": user_id,
                    "balance_drop_threshold": balance_drop_threshold,
                },
            }
        ),
        HTTPStatus.CREATED,
    )


@alerts_bp.route("delete", methods=["POST"])
@jwt_required()
def delete_alert():
    user_id = get_jwt_identity()
    data = request.get_json()
    alert_id = data.get("alert_id")

    if not alert_id:
        return jsonify({"msg": "Missing alert ID."}), HTTPStatus.BAD_REQUEST

    alert = Alert.query.filter_by(id=alert_id, user_id=user_id).first()
    if not alert:
        return jsonify({"msg": "Alert not found."}), HTTPStatus.NOT_FOUND

    db.session.delete(alert)
    db.session.commit()

    return jsonify({"msg": "Alert deleted successfully."}), HTTPStatus.OK


@alerts_bp.route("list", methods=["GET"])
@jwt_required()
def list_alerts():
    user_id = get_jwt_identity()
    alerts = Alert.query.filter_by(user_id=user_id).all()
    alerts_list = [
        {
            "id": alert.id,
            "user_id": alert.user_id,
            "target_amount": alert.target_amount,
            "alert_threshold": alert.alert_threshold,
            "balance_drop_threshold": alert.balance_drop_threshold,
            "created_at": alert.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }
        for alert in alerts
    ]
    return jsonify({"data": alerts_list}), HTTPStatus.OK
