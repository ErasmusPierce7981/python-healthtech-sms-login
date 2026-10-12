from health_login import LoginRequest, verify_login


class FakeClient:
    def __init__(self, verification=True):
        self.verification = verification
        self.calls = []

    def call(self, method, path, payload):
        self.calls.append((method, path, payload))
        if path == "/v1/auth/phone/verify":
            if not self.verification:
                from infrai_client import InfraiError
                raise InfraiError("CODE_REJECTED", {}, 400)
            return {"verified": True}
        return {"session_id": "session-1"}


def test_verified_code_creates_patient_session():
    client = FakeClient()
    result = verify_login(LoginRequest("patient-7", "+15551234567", "246810"), client)
    assert result.authenticated is True
    assert result.session == {"session_id": "session-1"}
    assert client.calls[1][2]["user_id"] == "patient-7"


def test_rejected_code_does_not_create_session():
    client = FakeClient(verification=False)
    result = verify_login(LoginRequest("patient-7", "+15551234567", "000000"), client)
    assert result.authenticated is False
    assert len(client.calls) == 1

