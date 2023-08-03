Testing
=======
Use `pytest` to run the tests in [the tests directory](dinglehopper/tests):
```bash
virtualenv -p /usr/bin/python3 venv
. venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
pytest
```

## Test running examples
Only unit tests:
```bash
pytest -m "not integration"
```

Only integration tests:
```bash
pytest -m integration
```

All tests:
```bash
pytest
```

All tests with code coverage:
```bash
pytest --cov=dinglehopper --cov-report=html
```

Static code analysis:
```bash
pytest -k "not test" --mypy
pytest -k "not test" --ruff
```
