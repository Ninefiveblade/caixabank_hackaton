from http import HTTPStatus

import bcrypt
from flask import Blueprint, jsonify, request, Response
from flask_jwt_extended import create_access_token

from app import db
from app.models import User
from app.utils import check_email

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Register a new user.

    Request Body:
    - email (str): The email of the user.
    - password (str): The password of the user.
    - name (str): The name of the user.

    Responses:
    - 201 Created: User successfully registered.
    - 400 Bad Request: If any required field is missing or invalid.
    - 400 Bad Request: If the email already exists.
    - 400 Bad Request: If the email is invalid.
    """
    data = request.get_json()
    if not data or not all(key in data for key in ("email", "password", "name")):
        return Response("All fields are required.", status=HTTPStatus.BAD_REQUEST)

    email = data["email"]
    if User.query.filter_by(email=email).first():
        return Response("Email already exists.", status=HTTPStatus.BAD_REQUEST)

    if not check_email(email):
        return Response(f"Invalid email: {email}", status=HTTPStatus.BAD_REQUEST)

    if None in data.values():
        return Response("No empty fields allowed.", status=HTTPStatus.BAD_REQUEST)

    hashed_password = bcrypt.hashpw(
        data["password"].encode("utf-8"), bcrypt.gensalt(12)
    ).decode("utf-8")
    user = User(name=data["name"], email=data["email"], hashed_password=hashed_password)
    db.session.add(user)
    db.session.commit()

    return (
        jsonify(
            {"name": user.name, "hashedPassword": hashed_password, "email": user.email}
        ),
        HTTPStatus.CREATED,
    )


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Authenticate a user and return a JWT token.

    Request Body:
    - email (str): The email of the user.
    - password (str): The password of the user.

    Responses:
    - 200 OK: User successfully authenticated.
    - 400 Bad Request: If any required field is missing.
    - 401 Unauthorized: If the credentials are invalid.
    """
    data = request.get_json()
    if not data or not all(key in data for key in ("email", "password")):
        return Response("All fields are required.", status=HTTPStatus.BAD_REQUEST)

    email = data.get("email")
    user = User.query.filter_by(email=email).first()
    if any(None in data.values()):
        return Response("Bad credentials.", status=HTTPStatus.BAD_REQUEST)
    if user is None:
        return (
            Response(f"User not found for the given email: ({email})", status=HTTPStatus.NOT_FOUND),
            HTTPStatus.BAD_REQUEST,
        )

    if not bcrypt.checkpw(
        data["password"].encode("utf-8"), user.hashed_password.encode("utf-8")
    ):
        return Response(
            "Bad credentials.", status=HTTPStatus.UNAUTHORIZED
        )

    token = create_access_token(identity=str(user.id))
    return jsonify({"token": token}), HTTPStatus.OK
