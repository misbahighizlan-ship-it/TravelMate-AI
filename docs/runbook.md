# Incident runbook

## Severity
- Low: one specialist fails but a safe fallback is returned.
- Medium: a required specialist repeatedly fails; workflow health is DEGRADED.
- High: suspected secret exposure or unsafe output; stop using the affected key, rotate it, preserve sanitized logs, and notify the project owner.

## Example: Budget Agent failure
1. Identify: dashboard shows `budget: FAILED`, health `DEGRADED`, correlation ID, two attempts.
2. Contain: keep the failed budget marked unavailable; do not represent it as a verified quote.
3. Diagnose: use correlation ID to inspect event names, durations, error code and attempt count. Logs exclude raw exceptions and secrets.
4. Recover: fix the node or dependency, rerun tests, and provide manual budget review if needed.
5. Resolve: document cause and fix, close incident only after a successful rerun.

For demonstration, check “Simuler une panne du Budget Agent” before submitting. This is an intentional test fault, not a live production incident.
