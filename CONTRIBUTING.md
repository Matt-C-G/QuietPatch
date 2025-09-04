## Developer quickstart

```bash
brew install uv
uv venv --python 3.12
source .venv/bin/activate
uv pip install -e ".[dev]"
pytest -q
```

