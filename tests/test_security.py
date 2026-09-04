import pytest
from flask import Flask

from buska_core.security import check_production_security, setup_security_headers


@pytest.fixture()
def app():
    app = Flask(__name__)
    app.config["JWT_SECRET_KEY"] = "a" * 40

    @app.route("/ping")
    def ping():
        return "pong"

    return app


def test_default_csp_is_self_only(app):
    setup_security_headers(app)
    resp = app.test_client().get("/ping")
    csp = resp.headers["Content-Security-Policy"]
    assert "script-src 'self';" in csp
    assert "unsafe-inline" not in csp
    assert "unsafe-eval" not in csp


def test_opt_in_unsafe_flags_add_expected_tokens(app):
    setup_security_headers(app, allow_unsafe_inline_scripts=True, allow_unsafe_eval=True)
    csp = app.test_client().get("/ping").headers["Content-Security-Policy"]
    assert "'unsafe-inline'" in csp
    assert "'unsafe-eval'" in csp


def test_csp_extra_sources_are_appended_per_directive(app):
    setup_security_headers(
        app,
        csp_extra_sources={
            "img-src": ["https://tile.openstreetmap.org"],
            "connect-src": ["https:"],
        },
    )
    csp = app.test_client().get("/ping").headers["Content-Security-Policy"]
    assert "img-src 'self' data: https://tile.openstreetmap.org;" in csp
    assert "connect-src 'self' https:;" in csp


def test_standard_headers_present(app):
    setup_security_headers(app)
    headers = app.test_client().get("/ping").headers
    assert headers["X-Content-Type-Options"] == "nosniff"
    assert headers["X-Frame-Options"] == "DENY"


def test_hsts_only_set_outside_debug(app):
    setup_security_headers(app)
    app.config["DEBUG"] = True
    assert "Strict-Transport-Security" not in app.test_client().get("/ping").headers

    app.config["DEBUG"] = False
    assert "Strict-Transport-Security" in app.test_client().get("/ping").headers


def test_check_production_security_flags_weak_config():
    app = Flask(__name__)
    app.config["DEBUG"] = True
    app.config["JWT_SECRET_KEY"] = "short"
    app.config["CORS_ORIGINS"] = "*"

    warnings = check_production_security(app)

    assert any("DEBUG" in w for w in warnings)
    assert any("JWT_SECRET_KEY" in w for w in warnings)
    assert any("CORS" in w for w in warnings)
    assert any("SESSION_COOKIE_SECURE" in w for w in warnings)


def test_check_production_security_clean_config_has_no_warnings():
    app = Flask(__name__)
    app.config["DEBUG"] = False
    app.config["JWT_SECRET_KEY"] = "a" * 40
    app.config["CORS_ORIGINS"] = "https://example.com"
    app.config["SESSION_COOKIE_SECURE"] = True

    assert check_production_security(app) == []
