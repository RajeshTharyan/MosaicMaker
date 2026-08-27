# Contributing

This is a personal portfolio repository, not a community product. Small, focused changes are welcome if they keep the app honest about what it does.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
pytest
streamlit run streamlit_mosaic.py
```

## Guidelines

- Put geometry, validation, and PNG encoding in `mosaic/`. Do not import Streamlit from that package — tests and CI depend on it staying headless.
- Keep `streamlit_mosaic.py` as the UI entry point (Dev Container and Streamlit Cloud both call this filename).
- Prefer tests in `tests/test_grid.py` for anything that does not need a browser or a network.
- Do not add a fake hosted-demo URL. There is none.

Issues and pull requests that fix bugs, tighten tests, or document real limits are more useful than new collage features.
