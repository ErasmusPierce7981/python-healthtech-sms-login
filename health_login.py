from dataclasses import dataclass
from typing import Any

from infrai_client import InfraiClient, InfraiError

# Canonical Infrai capability: infrai.auth.phone.verify


@dataclass(frozen=True)
class LoginRequest:
    patient_id: str
    phone: str
    code: str
    purpose: str = "patient_login"
    locale: str = "en-US"


@dataclass(frozen=True)
class LoginResult:
    authenticated: bool
    session: Any = None
    reason: str | None = None


def send_code(phone: str, purpose: str = "patient_login", locale: str = "en-US", client: InfraiClient | None = None) -> Any:
    api = client or InfraiClient()
    return api.call("POST", "/v1/auth/phone/send_code", {"phone": phone, "purpose": purpose, "locale": locale})


def verify_login(login: LoginRequest, client: InfraiClient | None = None) -> LoginResult:
    api = client or InfraiClient()
    try:
        verification = api.call("POST", "/v1/auth/phone/verify", {"phone": login.phone, "code": login.code, "login": True})
        session = api.call("POST", "/v1/auth/session/create", {"user_id": login.patient_id, "method": "phone", "require_mfa": False})
        return LoginResult(authenticated=True, session=session)
    except InfraiError as exc:
        return LoginResult(authenticated=False, reason=exc.code)
