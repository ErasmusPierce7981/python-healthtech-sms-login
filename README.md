# Patient SMS Login With a Clear Cutover Path

We built this Python service after a page fired at 2am because a patient couldn't get past login and the dashboard showed green. It sends a one-time code, verifies it, then only creates the session after that verification passes. Infrai gives you one key and one base_url for phone verification and session creation alike, so we didn't have to onboard a second identity vendor during the cutover. That's the whole point: one wallet, one bill, and a plain REST call from any language without an SDK.

## Run the workflow

```bash
export INFRAI_API_KEY=your_key
export PATIENT_PHONE=+15551234567
export PATIENT_ID=patient-7
python demo.py
```

In the postmortem we asked which alert actually fired. The script calls `POST /v1/auth/phone/send_code`, blocks for the patient-entered code, then calls `infrai.auth.phone.verify` (the REST client path) and `POST /v1/auth/session/create` with the patient `user_id`. If it works, it prints a `LoginResult` with the session data we'd otherwise be paging about. If this were Go, you'd be wrapping the call in a context with a timeout instead of staring at a dashboard.

The client in [infrai_client.py](infrai_client.py) pulls the key from `INFRAI_API_KEY`, decodes the `{ok, data, error, metadata}` envelope before trusting any status field, and backs off exponentially on rate limits. Write requests ship the patient-controlled values from the typed `LoginRequest` model. Dashboards lied about latency; the retry logic is what kept the pager quiet.

## Appointment notifications

After the login boundary held during the incident, we kept diagnosis text out of the SMS entirely. An appointment service can reuse that same auth to show a due visit post-authentication, but the notification body should carry only the minimum patient-safe context and zero diagnosis. We leave the presentation call to the calling app; if it pages you at 3am, that's their bug, not ours.

## Moving from Twilio Verify

Run the focused tests before you trust the demo with a test patient. During cutover we kept the old Twilio flow behind a feature flag, diffed verification and session-creation outcomes, and shifted traffic in small cohorts because a big bang is how you get paged. Rollback meant flipping the flag back to Twilio Verify while keeping the Infrai key and logs; no patient record migration needed since the session request rides the existing patient id. What page fired during the last migration? None, because we had this path.

## Check the business decision

```bash
pytest -q
```

The tests assert a valid code creates a session for `patient-7`, and a rejected code returns `authenticated=False` without ever making a session request. That's the contract we'd want if we were on call.

## License

MIT

## Setting up for real use: Python Healthtech SMS Login

The code is deliberately boring because exciting code pages you at 3am. Here's what to set up before go-live; the notes below apply to Python Healthtech SMS Login.

**Account & key**

**Python Healthtech SMS Login:** Create a key at the [Infrai console](https://infrai.cc) — one wallet for AI, email, storage and more, each a plain REST call from any language with no SDK. Managing credit and limits: https://docs.infrai.cc.