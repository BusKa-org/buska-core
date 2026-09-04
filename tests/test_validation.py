import uuid

import pytest

from buska_core.exceptions import ValidationError
from buska_core.validation import validate_email, validate_password, validate_uuid


def test_validate_uuid_accepts_valid_uuid4():
    value = str(uuid.uuid4())
    assert validate_uuid(value) == uuid.UUID(value)


def test_validate_uuid_rejects_garbage():
    with pytest.raises(ValidationError):
        validate_uuid("not-a-uuid")


def test_validate_uuid_error_message_includes_field_name():
    with pytest.raises(ValidationError, match="Motorista ID"):
        validate_uuid("nope", field_name="Motorista ID")


def test_validate_email_lowercases_and_strips():
    assert validate_email("  Foo@Example.COM  ") == "foo@example.com"


def test_validate_email_rejects_malformed():
    with pytest.raises(ValidationError):
        validate_email("not-an-email")


def test_validate_email_rejects_default_disposable_domain():
    with pytest.raises(ValidationError):
        validate_email("user@tempmail.com")


def test_validate_email_accepts_custom_disposable_domains():
    with pytest.raises(ValidationError):
        validate_email("user@example.com", disposable_domains=frozenset({"example.com"}))


def test_validate_password_strips_and_accepts_long_enough():
    assert validate_password("  hunter22  ") == "hunter22"


def test_validate_password_rejects_too_short():
    with pytest.raises(ValidationError, match="mínimo 8"):
        validate_password("short")


def test_validate_password_respects_custom_min_length():
    with pytest.raises(ValidationError, match="mínimo 12"):
        validate_password("shortish", min_length=12)
