# Testing with pytest

Run all tests:
- `pytest`

Formatted report.html file:
- `pip install pytest-html`
- `pytest --html=./tests/reports/report.html --self-contained-html >/dev/null`

Isolated test with logs (-s):
- `python -m pytest -s path/filename.py`
