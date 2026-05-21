# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run the app (serves at http://127.0.0.1:8000)
shiny run app-core.py

# Install dependencies
pip install -e .
pip install -e ".[dev]"   # includes pytest, black, flake8, mypy

# Tests / linting
pytest
black .
flake8 .
mypy .
```

## Architecture

This is a **Posit Shiny for Python** web app that combines interactive data visualization with AI-powered chart analysis via Claude.

**Entry point:** `app-core.py` — defines the full Shiny UI and server. It loads `mtcars.csv`, provides X/Y axis selectors, renders a Plotly scatter plot (bubble size = weight, color = region), and exposes an "Explain Plot" button.

**AI analysis:** `explain_plot.py` — invoked by the "Explain Plot" button. It captures the current matplotlib/Plotly figure as a base64 PNG image, opens a Shiny modal dialog containing a chat interface, and streams responses from Claude via `chatlas.ChatAnthropic`. Follow-up questions are supported within the modal session.

**Shared data:** `shared.py` — loads `penguins.csv` into a pandas DataFrame. Currently imported but not used in the main app; available for extension.

**Datasets:** `mtcars.csv` (33 rows, automotive metrics) and `penguins.csv` (345 rows, Palmer penguins). The main app uses mtcars; column names are remapped to human-readable labels (e.g., `"mpg"` → `"Miles per Gallon"`).

## Environment

Requires an `ANTHROPIC_API_KEY` environment variable (loaded via `python-dotenv`). Create a `.env` file in the project root:

```
ANTHROPIC_API_KEY=sk-ant-...
```

## Key Implementation Notes

- **`PlotWidget`** in `app-core.py` wraps matplotlib figures to provide a `write_image()` method expected by `explain_plot.py`.
- Each browser session gets a UUID; multiple "Explain Plot" invocations within a session use incrementing counters as chat IDs.
- The Claude system prompt in `explain_plot.py` instructs the model to identify patterns, correlations, outliers, domain-specific context, and suggest dashboard improvements — stay consistent with that framing when modifying the prompt.
- Python 3.9–3.12 is supported (constrained in `pyproject.toml`).
