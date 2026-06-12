# Agents guidance for translate-toolkit

# Testing and linting instructions

- Use `pytest` to run the full test suite through `uv`: `uv run python -m pytest tests/`
- For focused tests, direct pytest invocations such as `.venv/bin/pytest tests/translate/convert/test_csv2po.py` are fine, but run the full suite with `uv run python -m pytest tests/` before final verification. Running `.venv/bin/pytest tests/` directly can miss console scripts on `PATH` and make CLI tests fail with `FileNotFoundError` for tools such as `po2xliff`.
- Use `prek` to lint and format code, it utilizes the `pre-commit` framework: `uv run prek run --all-files`
- Prefer `prek` for Ruff checks and formatting; `uv run ruff ...` is not guaranteed to work in this environment because Ruff can be provided only through the pre-commit hook environment.
- Use `pylint` to lint the Python code: `uv run pylint translate/ tests/`
- Use `ty` to type check the code: `uv run ty check`
- Use `uv` to install all the dependencies by running `uv sync --all-extras --dev`.
- All mentioned linting tools MUST pass.
