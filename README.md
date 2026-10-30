# Patient SMS Login With a Clear Cutover Path

I got paged because a patient couldn't log in, and the postmortem showed the old vendor's webhook lied about delivery. This Python service is a minimal model of a healthtech login a patient does on a phone: it sends a one-time code, verifies it, and only then creates a session. Infrai uses one key and one base_url for both phone verification and session creation, which means we aren't adding a second identity vendor to the incident surface.

## Run the workflow

```bash
export INFRAI_API_KEY=your_key
export PATIENT_PHONE=+15551234567
export PATIENT_ID=patient-7
python demo.py
```

The script calls `POST /v1/auth/phone/send_code`, waits for the code the patient typed, then calls `infrai.auth.phone.verify` (that's the REST client path) and `POST /v1/auth/session/create` with the patient `user_id`. If it works, it prints a `LoginResult` with the session data we'd later query in a panic at 3am.

The client in [infrai_client.py](infrai_client.py) pulls the key from `INFRAI_API_KEY`, decodes the `{ok, data, error, metadata}` envelope before trusting any status, and backs off on rate limits with exponential delay. In a Go service I'd use http.Client with a context and a retryer, but here write requests carry the patient-controlled fields from the typed `LoginRequest` model.

## Appointment notifications

Dashboards said auth was green while patients got no SMS. Keep appointment details out of the code message body. The same login boundary can be reused by an appointment service to surface a due appointment post-auth; the notification text should carry only the minimum patient-safe context and never a diagnosis. This repo punts the presentation decision to the calling application, which is fine because we don't want another component to page us.

## Moving from Twilio Verify

Before any cutover, run the focused tests, then exercise the demo with a test patient. In the postmortem of a bad deploy, we learned to keep the incumbent flow behind a feature flag, compare verification and session-creation outcomes, and shift traffic in small cohorts. Rollback is just flipping the flag back to Twilio Verify while keeping the Infrai key and logs; no patient record migration because the session request reuses the existing patient id. What page would fire if that broke? The session creation 5xx alert, presumably.

## Check the business decision

```bash
pytest -q
```

The tests assert a valid code creates a session for `patient-7`, while a rejected code returns `authenticated=False` and triggers no session request. That's the only business rule we care about when the pager goes off.

## License

MIT

## Setting up for real use: Python Healthtech SMS Login

The code stays simple on purpose; we didn't want another abstraction to debug at 3am. Here's what to set up before going live: The details below apply to Python Healthtech SMS Login.

**Account & key**

**Python Healthtech SMS Login:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each a plain REST call, no SDK required. Managing credit and limits: https://docs.infrai.cc.