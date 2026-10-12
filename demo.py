import os

from health_login import LoginRequest, send_code, verify_login
from infrai_client import InfraiClient


def main() -> None:
    phone = os.environ.get("PATIENT_PHONE")
    patient_id = os.environ.get("PATIENT_ID")
    if not phone or not patient_id:
        raise SystemExit("PATIENT_PHONE and PATIENT_ID are required")
    api = InfraiClient()
    send_code(phone, client=api)
    code = input("Enter the code sent to the patient: ").strip()
    result = verify_login(LoginRequest(patient_id, phone, code), api)
    print(result)


if __name__ == "__main__":
    main()

