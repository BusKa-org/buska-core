"""Security headers shared across Flask apps.

Dropped the original SecurityConfig class (SESSION_COOKIE_*, JWT_*_EXPIRES_*,
rate-limit strings, CORS_MAX_AGE) rather than moving it verbatim — most of
it was dead (JWT expiry and CORS max-age are already set elsewhere; no
rate limiter exists anywhere to configure). SESSION_COOKIE_* was the one
real gap: declared but never applied, so setup_security_headers below
applies it now instead of just carrying the constant forward.
"""

from collections.abc import Sequence

from flask import Flask, Response


def setup_security_headers(
    app: Flask,
    *,
    csp_extra_sources: dict[str, Sequence[str]] | None = None,
    allow_unsafe_inline_scripts: bool = False,
    allow_unsafe_inline_styles: bool = False,
    allow_unsafe_eval: bool = False,
    secure_session_cookies: bool = True,
) -> None:
    """Register standard security headers on every response.

    Defaults to a strict CSP ('self' only) and secure session cookies;
    opt into 'unsafe-inline'/'unsafe-eval' or extra CSP sources explicitly
    via the params instead of them being baked in unconditionally.
    """
    if secure_session_cookies:
        app.config.setdefault("SESSION_COOKIE_SECURE", True)
        app.config.setdefault("SESSION_COOKIE_HTTPONLY", True)
        app.config.setdefault("SESSION_COOKIE_SAMESITE", "Lax")
    csp_extra_sources = csp_extra_sources or {}

    def directive(name: str, base: Sequence[str]) -> str:
        return " ".join([*base, *csp_extra_sources.get(name, ())])

    script_base = ["'self'"]
    if allow_unsafe_inline_scripts:
        script_base.append("'unsafe-inline'")
    if allow_unsafe_eval:
        script_base.append("'unsafe-eval'")

    style_base = ["'self'"] + (["'unsafe-inline'"] if allow_unsafe_inline_styles else [])

    script_src = directive("script-src", script_base)
    style_src = directive("style-src", style_base)
    img_src = directive("img-src", ["'self'", "data:"])
    connect_src = directive("connect-src", ["'self'"])

    @app.after_request
    def add_security_headers(response: Response) -> Response:
        response.headers["Content-Security-Policy"] = (
            f"default-src 'self'; "
            f"script-src {script_src}; "
            f"style-src {style_src}; "
            f"img-src {img_src}; "
            f"font-src 'self' data:; "
            f"connect-src {connect_src}; "
            f"frame-ancestors 'self'; "
        )
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = (
            "geolocation=(self), microphone=(), camera=(), payment=()"
        )
        if not app.config.get("DEBUG"):
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )
        return response


def check_production_security(app: Flask) -> list[str]:
    """Return a list of production-readiness security warnings for app.config."""
    warnings: list[str] = []

    if app.config.get("DEBUG"):
        warnings.append("DEBUG mode is enabled - MUST be disabled in production")

    jwt_secret = app.config.get("JWT_SECRET_KEY", "")
    if len(jwt_secret) < 32:
        warnings.append("JWT_SECRET_KEY is too short - use at least 32 characters")

    cors_origins = app.config.get("CORS_ORIGINS", "*")
    if cors_origins == "*":
        warnings.append("CORS allows all origins - restrict to specific domains in production")

    if not app.config.get("SESSION_COOKIE_SECURE"):
        warnings.append("SESSION_COOKIE_SECURE not set - cookies should require HTTPS")

    return warnings
