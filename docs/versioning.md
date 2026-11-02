# Versioning Policy — TravelMate AI

## Current version

The project version is `0.2.0`. This is an MVP and is not yet a published GitHub release.

## Semantic Versioning

Versions use `MAJOR.MINOR.PATCH`:

- **MAJOR:** incompatible change to the API or workflow.
- **MINOR:** new backward-compatible capability.
- **PATCH:** backward-compatible bug fix.

Before version `1.0.0`, interfaces and behavior may change as the MVP develops.

## Release checklist

1. Run the test suite locally.
2. Confirm GitHub Actions is green on the exact commit to release.
3. Update `VERSION`, `CHANGELOG.md`, and Agent Cards if the project version changes.
4. Create a Git tag using the `v` prefix, for example `v0.2.0`.
5. Publish release notes that describe what changed and any known limitations.

Do not create a release tag for an untested commit. Documentation-only edits do not automatically require a new application version.