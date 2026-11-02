# Incident Runbook — TravelMate AI v0.2.0

## Scope

This runbook describes how to handle failures in the TravelMate AI MVP. The current app records agent statuses, durations, errors, retry events, and correlation IDs. It does not send automatic alerts or provide an automatic Kill Switch.

## Severity

- **Low:** one agent fails, but a visible fallback is returned.
- **Medium:** a required agent fails after retry; workflow health becomes `DEGRADED`.
- **High:** suspected secret exposure or unsafe output. Stop using the affected service or key, rotate the key, and notify the project owner.

## Incident response

1. **Detection:** check the dashboard for `FAILED`, `DEGRADED`, or an incident message.
2. **Containment:** do not rely on the failed agent’s result. For a local demo, stop the app with `Ctrl+C` if output appears unsafe. No automatic Kill Switch is implemented.
3. **Diagnosis:** use the correlation ID to review agent statuses, durations, retry events, and sanitized error codes. Never put API keys or database connection strings in logs or screenshots.
4. **Remediation:** check the responsible agent and its configuration; make one targeted fix, then run the tests.
5. **Recovery:** submit a new request. Confirm the required agents succeed and the workflow returns to `HEALTHY`.
6. **Review:** record the cause and fix. Keep the incident open until a successful rerun is confirmed.

## Demonstration: simulated Budget Agent failure

1. Select “Simuler une panne du Budget Agent” in the dashboard.
2. Submit a sample trip request.
3. Confirm `budget: FAILED`, workflow health `DEGRADED`, two attempts, and a visible fallback.
4. Explain that this is a deliberate classroom simulation, not a real production incident.

## Current limitations

- Alerts and human escalation are manual.
- There is no automatic rollback or Kill Switch.
- Budget allocations are not verified market prices.
- The app has no live weather, transport, booking, or availability source.