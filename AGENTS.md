# Agents guidance for translate-toolkit

# Testing and linting instructions

- Use `pytest` to run the testsuite: `pytest tests/`
- Use `prek` to lint code, it utilizes the `pre-commit` framework: `prek run --all-files`
- Use `pylint` to lint the Python code: `pylint translate/ tests/`
- Use `ty` to type check the code: `ty check`
- Use `uv` to install all the dependencies as `uv sync --all-extras --dev`.
- All mentioned linting tools MUST pass.
