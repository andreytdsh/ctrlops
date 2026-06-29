# Installation

## Local Python

Clone the repository:

```bash
git clone https://github.com/andreytdsh/ctrlops.git
cd ctrlops
```

Create a virtual environment and install the CLI/Web app:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

For development dependencies:

```bash
pip install -e ".[dev]"
```

Windows PowerShell:

```powershell
git clone https://github.com/andreytdsh/ctrlops.git
cd ctrlops
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

## pipx

From GitHub:

```bash
pipx install git+https://github.com/andreytdsh/ctrlops.git
ctrlops --help
```

From a checked-out repository:

```bash
pipx install .
ctrlops --help
```

## Docker Compose

```bash
git clone https://github.com/andreytdsh/ctrlops.git
cd ctrlops
docker compose up --build
```

Open `http://localhost:8000`.
