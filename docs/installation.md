# Installation

## Local Python

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

## pipx

From a checked-out repository:

```bash
pipx install .
ctrlops --help
```

## Docker Compose

```bash
docker compose up --build
```

Open `http://localhost:8000`.
