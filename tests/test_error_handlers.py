def test_not_found_error_returns_404_with_error_contract(client):
    resp = client.get("/not-found")
    assert resp.status_code == 404
    body = resp.get_json()
    assert body["error"]["code"] == "NOT_FOUND"
    assert body["error"]["message"] == "Rota não encontrada"
    assert "request_id" in body["error"]


def test_validation_error_includes_details(client):
    resp = client.get("/validation")
    assert resp.status_code == 400
    body = resp.get_json()
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert body["error"]["details"] == {"nome": "obrigatório"}


def test_forbidden_error_returns_403(client):
    resp = client.get("/forbidden")
    assert resp.status_code == 403
    assert resp.get_json()["error"]["code"] == "FORBIDDEN"


def test_unauthorized_error_returns_401(client):
    resp = client.get("/unauthorized")
    assert resp.status_code == 401
    assert resp.get_json()["error"]["code"] == "UNAUTHORIZED"


def test_conflict_error_includes_field(client):
    resp = client.get("/conflict")
    assert resp.status_code == 409
    body = resp.get_json()
    assert body["error"]["code"] == "CONFLICT"
    assert body["error"]["field"] == "sigla"


def test_404_route_returns_http_error_contract(client):
    resp = client.get("/this-route-does-not-exist")
    assert resp.status_code == 404
    body = resp.get_json()
    assert body["error"]["code"] == "HTTP_ERROR"


def test_unhandled_exception_returns_500_without_leaking_details(client):
    resp = client.get("/boom")
    assert resp.status_code == 500
    body = resp.get_json()
    assert body["error"]["code"] == "INTERNAL_ERROR"
    assert "unexpected" not in body["error"]["message"]


def test_request_id_echoes_incoming_header(client):
    resp = client.get("/not-found", headers={"X-Request-ID": "abc-123"})
    assert resp.get_json()["error"]["request_id"] == "abc-123"


def test_jwt_missing_token_returns_401_with_reason(app):
    from flask_jwt_extended import jwt_required

    @app.route("/protected")
    @jwt_required()
    def protected():
        return {"ok": True}

    resp = app.test_client().get("/protected")
    assert resp.status_code == 401
    body = resp.get_json()
    assert body["error"]["code"] == "UNAUTHORIZED"
    assert "reason" in body["error"]["details"]
