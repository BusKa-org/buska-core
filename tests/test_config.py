import pytest

from buska_core.config import ConfigurationError, Settings


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    for key in (
        "FLASK_ENV",
        "DB_USER",
        "DB_PASSWORD",
        "DB_HOST",
        "DB_PORT",
        "DB_NAME",
        "JWT_SECRET_KEY",
        "JWT_EXPIRES_HOURS",
        "MAIL_SERVER",
        "CORS_ORIGINS",
        "FIREBASE_CREDENTIALS",
    ):
        monkeypatch.delenv(key, raising=False)


def test_development_defaults_dont_raise():
    settings = Settings.load()
    assert settings.DEBUG is True
    assert settings.DB_NAME == "buska_db"
    assert settings.CORS_ORIGINS == "*"


def test_production_with_defaults_raises(monkeypatch):
    monkeypatch.setenv("FLASK_ENV", "production")
    with pytest.raises(ConfigurationError, match="JWT_SECRET_KEY"):
        Settings.load()


def test_production_with_strong_secret_and_explicit_values_is_valid(monkeypatch):
    monkeypatch.setenv("FLASK_ENV", "production")
    monkeypatch.setenv("JWT_SECRET_KEY", "a" * 32)
    monkeypatch.setenv("DB_USER", "u")
    monkeypatch.setenv("DB_PASSWORD", "p")
    monkeypatch.setenv("DB_HOST", "h")
    monkeypatch.setenv("DB_NAME", "n")
    monkeypatch.setenv("CORS_ORIGINS", "https://example.com")

    settings = Settings.load()
    assert settings.DEBUG is False
    assert settings.JWT_SECRET_KEY == "a" * 32


def test_invalid_cors_origin_raises_in_production(monkeypatch):
    monkeypatch.setenv("FLASK_ENV", "production")
    monkeypatch.setenv("JWT_SECRET_KEY", "a" * 32)
    monkeypatch.setenv("DB_USER", "u")
    monkeypatch.setenv("DB_PASSWORD", "p")
    monkeypatch.setenv("DB_HOST", "h")
    monkeypatch.setenv("DB_NAME", "n")
    monkeypatch.setenv("CORS_ORIGINS", "not-a-url")

    with pytest.raises(ConfigurationError, match="CORS_ORIGINS"):
        Settings.load()


def test_subclass_fields_are_covered_by_a_single_validation_pass(monkeypatch):
    monkeypatch.setenv("FLASK_ENV", "production")
    monkeypatch.setenv("JWT_SECRET_KEY", "a" * 32)
    monkeypatch.setenv("DB_USER", "u")
    monkeypatch.setenv("DB_PASSWORD", "p")
    monkeypatch.setenv("DB_HOST", "h")
    monkeypatch.setenv("DB_NAME", "n")
    monkeypatch.setenv("CORS_ORIGINS", "https://example.com")

    class ClientSettings(Settings):
        def __init__(self):
            super().__init__()
            self.SOME_API_KEY = self._get_required("SOME_API_KEY")

    with pytest.raises(ConfigurationError, match="SOME_API_KEY"):
        ClientSettings.load()


def test_firebase_credentials_optional_and_none_by_default():
    assert Settings.load().FIREBASE_CREDENTIALS is None
