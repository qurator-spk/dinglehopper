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

# How to use pre-commit

This project optionally uses [pre-commit](https://pre-commit.com) to check commits. To use it:

- Install pre-commit, e.g. `pip install -r requirements-dev.txt`
- Install the repo-local git hooks: `pre-commit install`


# Releasing a new version

- Update `ocrd-tool.json`
- `git commit`
- `git tag vx.y.z`
- `git push && git push --tags`
- The GitHub Actions workflow `release` will now create
  a. a new release on GitHub and
  b. a new release on PyPI
- Currently requires a review for PYPI?
