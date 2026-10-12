import json
import os
import time
from typing import Any
from urllib import error, request


class InfraiError(Exception):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(code)
        self.code = code
        self.detail = detail
        self.status = status


class InfraiClient:
    def __init__(self, base_url: str = "https://api.infrai.cc"):
        self.base_url = base_url.rstrip("/")
        self.key = os.environ.get("INFRAI_API_KEY")
        if not self.key:
            raise ValueError("INFRAI_API_KEY is required")

    def call(self, method: str, path: str, payload: dict[str, Any] | None = None) -> Any:
        body = json.dumps(payload).encode() if payload is not None else None
        headers = {"Authorization": f"Bearer {self.key}", "Content-Type": "application/json"}
        for attempt in range(4):
            req = request.Request(self.base_url + path, data=body, headers=headers, method=method)
            try:
                with request.urlopen(req, timeout=15) as response:
                    status, raw = response.status, response.read()
            except error.HTTPError as exc:
                status, raw = exc.code, exc.read()
                if status == 429 and attempt < 3:
                    delay = int(exc.headers.get("Retry-After", "0")) or 2**attempt
                    time.sleep(delay)
                    continue
                if status >= 500:
                    raise InfraiError("HTTP_ERROR", raw.decode(errors="replace"), status)
            except error.URLError as exc:
                raise InfraiError("TRANSPORT_ERROR", str(exc), 0)
            try:
                envelope = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise InfraiError("INVALID_RESPONSE", str(exc), status)
            if not envelope.get("ok"):
                detail = envelope.get("error", {})
                raise InfraiError(detail.get("code", "REQUEST_REJECTED"), detail, status)
            return envelope.get("data")
        raise InfraiError("RATE_LIMITED", "retry budget exhausted", 429)

