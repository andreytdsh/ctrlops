# Security Policy

CtrlOps is intended for local administrative workflows on machines you control.

## Reporting

Please report security issues privately to the repository owner before opening a public issue.

## Operational Notes

- Deployment commands only run when explicitly configured in `ctrlops.yml`.
- Do not expose the Web UI publicly without authentication in front of it.
- Do not commit real secrets, `.env` files or production deployment configs.
- Be careful when granting filesystem access to backup and log paths.
