"""Generic input validators. CPF stays in the consumer app — Brazil-specific."""

import re
import uuid

from buska_core.exceptions import ValidationError

DEFAULT_DISPOSABLE_EMAIL_DOMAINS = frozenset(
    {
        "tempmail.com",
        "codgal.com",
        "quantyti.com",
        "virgilian.com",
        "throwaway.email",
        "guerrillamail.com",
        "10minutemail.com",
    }
)

_EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


def validate_uuid(value: str, field_name: str = "ID") -> uuid.UUID:
    """Validate UUID format, raising ValidationError on failure."""
    try:
        return uuid.UUID(value, version=4)
    except (ValueError, AttributeError, TypeError):
        raise ValidationError(f"{field_name} deve ser um UUID válido") from None


def validate_email(
    email: str,
    *,
    disposable_domains: frozenset[str] = DEFAULT_DISPOSABLE_EMAIL_DOMAINS,
) -> str:
    """Validate email format and reject disposable domains. Returns it lowercased."""
    email = email.strip().lower()

    if not _EMAIL_PATTERN.match(email):
        raise ValidationError("Formato de email inválido")

    if email.split("@")[1] in disposable_domains:
        raise ValidationError("Email de domínio descartável não é permitido")

    return email


def validate_password(password: str, *, min_length: int = 8, field_name: str = "Senha") -> str:
    """Validate a password meets a minimum length. Returns it stripped."""
    password = password.strip()

    if len(password) < min_length:
        raise ValidationError(f"{field_name} deve ter no mínimo {min_length} caracteres")

    return password
