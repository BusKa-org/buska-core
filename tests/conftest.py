import pytest
from flask import Flask
from flask_jwt_extended import JWTManager

from buska_core.error_handlers import register_error_handlers, register_jwt_handlers
from buska_core.exceptions import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
    ValidationError,
)


@pytest.fixture()
def app():
    app = Flask(__name__)
    app.config["JWT_SECRET_KEY"] = "test-secret"
    register_error_handlers(app)
    jwt = JWTManager(app)
    register_jwt_handlers(jwt)

    @app.route("/not-found")
    def raise_not_found():
        raise NotFoundError("Rota não encontrada")

    @app.route("/validation")
    def raise_validation():
        raise ValidationError("Campo inválido", details={"nome": "obrigatório"})

    @app.route("/forbidden")
    def raise_forbidden():
        raise ForbiddenError()

    @app.route("/unauthorized")
    def raise_unauthorized():
        raise UnauthorizedError()

    @app.route("/conflict")
    def raise_conflict():
        raise ConflictError("Já existe", field="sigla")

    @app.route("/boom")
    def raise_unexpected():
        raise RuntimeError("unexpected")

    return app


@pytest.fixture()
def client(app):
    return app.test_client()
