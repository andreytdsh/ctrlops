# Contributing

Thanks for improving CtrlOps.

## Local Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

## Checks

Run before opening a pull request:

```bash
python -m ruff check .
python -m pytest
```

## Security

Do not commit secrets, real `.env` files, production logs or private deployment configs.
