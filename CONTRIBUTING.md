# Contributing to Translate Toolkit

Thank you for your interest in contributing to the Translate Toolkit!

## Quick Start for Developers

### Prerequisites
- Git
- Python 3.10 or newer
- [uv](https://docs.astral.sh/uv/) (recommended package manager)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/translate/translate.git
   cd translate
   ```

2. Install all dependencies (creates a virtual environment in `.venv`):
   ```bash
   uv sync --all-extras --dev
   ```

3. Run the tests:
   ```bash
   make test
   ```

## How to Contribute

For detailed information about contributing, please see our [full contributing guide](https://docs.translatehouse.org/projects/translate-toolkit/en/latest/developers/contributing.html).

### Ways to Contribute
- **Testing** - Help test new candidate releases
- **Debugging** - Check bug reports and create tests
- **Developing** - Add features or fix bugs
- **Documenting** - Improve documentation

## Communication

- [Issue tracker](https://github.com/translate/translate/issues) - for bug reports, discussions, and questions
- [Discussions](https://github.com/translate/translate/discussions) - for general discussions and help

## Documentation

- [Developer Guide](https://docs.translatehouse.org/projects/translate-toolkit/en/latest/developers/developers.html)
- [Testing Guide](https://docs.translatehouse.org/projects/translate-toolkit/en/latest/developers/testing.html)
- [Style Guide](https://docs.translatehouse.org/projects/translate-toolkit/en/latest/developers/styleguide.html)
