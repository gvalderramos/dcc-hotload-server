# Introduction
**cpp-proj-maker** is a Python-based CLI tool that **bootstraps modern C++ project structures** with CMake, tests, documentation, and sensible defaults — so you can stop rewriting the same boilerplate over and over.

# Ways to Contribute
Before starting, please check the **Issues** tab to see if someone is already working on your idea or feature.

If not, feel free to:
1. Open a new issue to discuss your idea
2. Fork this repository
3. Create your changes
4. Submit a Pull Request for review

# Development Setup
You should have at least **Python >= 3.10 and < 3.15**.
You also need to have the [Poetry](https://python-poetry.org/docs/) installed.

Then, to run this repository is quite simple, you need just:
```bash
git clone <forked-repository.git>
poetry install
poetry run cpp-proj-maker
```
## Contributing to DCC Hotload Server

Thanks for your interest in contributing. This document explains how to
set up a development environment, run the server and tests, and how to add
new hooks or features.

## Ways to contribute

- Search or open an issue to discuss ideas before starting work.
- Fork the repository and create a feature branch.
- Open a focused pull request with tests and a clear description.

## Development setup

This project targets Python 3.8+. You can use either a virtualenv or
Poetry (there is a `pyproject.toml` in the repo).

Recommended steps using pip/venv:

```bash
git clone <your-fork-url>
cd dcc-hotload-server
poetry install
poetry run pytest
poetry run pre-commit run --all-files
```

If you use Poetry:

```bash
poetry install
```

## Running the server

Use the CLI entrypoint to start a DCC server. Examples:

```bash
python -m dcc_hotload_server.main --dcc mayapy --version 2024
python -m dcc_hotload_server.main --dcc hython --version 19.5
```

The CLI locates the DCC executable according to the hints in
`dcc_hotload_server/hooks/<dcc>.py`, then spawns a process that listens for
Python snippets over TCP.

## Sandbox clients

Example clients live in the `sandbox/` directory. Use them to send code to a
running server and inspect responses.

## Running tests and linters

Run tests with `pytest`:

```bash
pytest -q
```

Run pre-commit hooks (formatters / linters):

```bash
pre-commit run --all-files
# or with poetry
poetry run pre-commit run --all-files
```

## Adding a new DCC hook

Create a new module in `dcc_hotload_server/hooks/` and add a subclass of
`BaseHookServer` (see `mayapy.py` and `hython.py`):

1. Implement `hints(self, version)` returning a `SoftwareHint` with platform
	path hints.
2. Implement `initialize()` / `uninitialize()` if the DCC requires setup.
3. Add tests for any behavior unique to your hook.

The server dynamically imports `dcc_hotload_server.hooks.<name>` and uses the
first class in that module that subclasses `BaseHookServer`.

## Coding guidelines

- Follow PEP 8 and prefer readable, small, and testable changes.
- Use `black`/`isort` and run `pre-commit` hooks before submitting a PR.
- Prefer explicit exception handling and include tests for error cases.

## Pull request checklist

- [ ] Is there an issue describing the work? If not, consider opening one.
- [ ] Are new behaviors covered by tests where appropriate?
- [ ] Did you run linters and formatters (`pre-commit`)?
- [ ] Is the PR description clear: what, why, how?

Thank you — contributions are welcome. If you'd like help picking a
first issue, open one and tag it `good first issue`.