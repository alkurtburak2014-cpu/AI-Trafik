# AI-Trafik

Modernized, testable adaptive traffic light controller core.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
ai-trafik --help
pytest
```

## Project layout

- `src/ai_trafik/config.py`: controller configuration model.
- `src/ai_trafik/controller.py`: adaptive controller logic.
- `src/ai_trafik/service.py`: simple simulation service wrapper.
- `src/ai_trafik/cli.py`: command-line entry point.
- `tests/`: unit tests.
