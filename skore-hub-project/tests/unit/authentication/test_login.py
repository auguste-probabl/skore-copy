from datetime import datetime, timezone
from urllib.parse import urljoin

from httpx import (
    HTTPStatusError,
    NetworkError,
    RemoteProtocolError,
    Response,
    TimeoutException,
)
from pytest import mark, raises

from skore_hub_project.authentication import login as login_module

DATETIME_MIN = datetime.min.replace(tzinfo=timezone.utc).isoformat()
DATETIME_MAX = datetime.max.replace(tzinfo=timezone.utc).isoformat()

REFRESH_URL = "identity/oauth/token/refresh"
LOGIN_URL = "identity/oauth/device/login"
PROBE_URL = "identity/oauth/device/code-probe"
CALLBACK_URL = "identity/oauth/device/callback"
TOKEN_URL = "identity/oauth/device/token"


@mark.respx()
def test_login_with_api_key(monkeypatch, respx_mock):
    monkeypatch.setenv("SKORE_HUB_API_KEY", "<api-key>")

    assert login_module.credentials is None

    login_module.login()

    assert login_module.credentials is not None
    assert login_module.credentials() == {"X-API-Key": "<api-key>"}


@mark.respx()
def test_login_with_token(monkeypatch, respx_mock):
    monkeypatch.setattr(
        "skore_hub_project.authentication.token.open_webbrowser",
        lambda _: True,
    )
    respx_mock.get(LOGIN_URL).mock(
        Response(
            200,
            json={
                "authorization_url": "<url>",
                "device_code": "<device>",
                "user_code": "<user>",
            },
        )
    )
    respx_mock.get(PROBE_URL).mock(Response(200))
    respx_mock.post(CALLBACK_URL).mock(Response(200))
    respx_mock.get(TOKEN_URL).mock(
        Response(
            200,
            json={
                "token": {
                    "access_token": "D",
                    "refresh_token": "E",
                    "expires_at": DATETIME_MAX,
                }
            },
        )
    )

    assert login_module.credentials is None

    login_module.login()

    assert login_module.credentials is not None
    assert login_module.credentials() == {"Authorization": "Bearer D"}
