from buska_core.exceptions import (
    AppError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
    ValidationError,
)


def test_app_error_defaults():
    err = AppError("algo deu errado")
    assert err.status_code == 400
    assert err.code == "APP_ERROR"
    assert err.field is None
    assert str(err) == "algo deu errado"


def test_not_found_error_is_404():
    err = NotFoundError()
    assert err.status_code == 404
    assert err.code == "NOT_FOUND"
    assert err.message == "Recurso não encontrado"


def test_validation_error_carries_details():
    err = ValidationError("Dados inválidos", details={"nome": "obrigatório"})
    assert err.status_code == 400
    assert err.code == "VALIDATION_ERROR"
    assert err.details == {"nome": "obrigatório"}


def test_validation_error_defaults_details_to_empty_dict():
    err = ValidationError()
    assert err.details == {}


def test_forbidden_error_is_403():
    err = ForbiddenError()
    assert err.status_code == 403
    assert err.code == "FORBIDDEN"


def test_unauthorized_error_is_401():
    err = UnauthorizedError()
    assert err.status_code == 401
    assert err.code == "UNAUTHORIZED"


def test_conflict_error_carries_field():
    err = ConflictError("Já existe", field="sigla")
    assert err.status_code == 409
    assert err.code == "CONFLICT"
    assert err.field == "sigla"


def test_all_app_errors_are_app_error_subclasses():
    for cls in (NotFoundError, ValidationError, ForbiddenError, UnauthorizedError, ConflictError):
        assert issubclass(cls, AppError)
