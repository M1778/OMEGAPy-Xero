# OMEGAPy-Xero

Interactive AI assistant powered by OMEGAPy-XInter/Xero.

## Requirements

- Python 3.10 or higher
- pip

## Installation

```bash
# Clone the repository
git clone https://github.com/M1778/OMEGAPy-Xero.git
cd OMEGAPy-Xero

# Create a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Install core dependencies
pip install -e .

# Or install from requirements.txt
pip install -r requirements.txt
```

### Optional Dependency Groups

```bash
# Desktop GUI (Windows, PyQt6)
pip install -e ".[desktop]"

# ML features (local speech recognition, wake word)
pip install -e ".[ml]"

# Everything including desktop and ML
pip install -e ".[all]"

# Development tools
pip install -e ".[dev]"
```

## Running

### Web UI

```bash
python lucid_web.py
```

### Desktop GUI (Windows only)

```bash
python SoreUI/launch.py
```

### CLI

```bash
python run_lucid.py
```

## Configuration

Copy `config-sample.cfg` to `config.cfg` and fill in your API keys:

```bash
cp config-sample.cfg config.cfg
```

For the desktop GUI, settings are managed through the in-app Settings panel.

## Project Structure

```
OMEGAPy-Xero/
├── essentials/          # Core AI logic, API wrappers, prompts
├── SoreUI/              # PyQt6 desktop GUI
├── static/              # Web UI static assets
├── templates/           # Flask HTML templates
├── models/              # ML model files
├── lucid_web.py         # Flask web server
├── run_lucid.py         # CLI interface
├── pyproject.toml       # Project metadata & dependencies
└── requirements.txt     # Pinned dependencies
```

## Contributing

This project has a lot of bugs. Contributions are welcome.
