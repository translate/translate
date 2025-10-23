# Copilot Instructions for translate-toolkit

# Existing documentation

Follow existing contributor documentation in `docs/developers/`.

## Code Style and Standards

- Follow PEP 8 standards
- Use type annotations

### Linting and Formatting

- Pre-commit hooks are configured (`.pre-commit-config.yaml`)
- Use pylint for Python code quality
- Follow existing code formatting patterns
- Run `pre-commit run --all-files` before committing
- Type check new code with `mypy`

## Documentation

- Document new feature in ``docs/``

### Dependencies

- Manage dependencies in `pyproject.toml`
- Use dependency groups for different environments (dev, test, docs, etc.)
- Keep dependencies up to date with security considerations
