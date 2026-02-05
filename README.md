# DCC Hotload Server

Lightweight TCP server that launches a DCC Python interpreter in batch mode
and accepts Python code over a socket for rapid development and hotloading
in DCC environments (e.g., Maya, Houdini).

## Features
- Start a DCC Python process (mayapy / hython) that listens for small Python
	snippets to execute.
- Capture stdout/stderr from executed snippets and return results to clients.
- Hooks for adding DCC-specific initialization and teardown logic.

## Repository layout

- `dcc_hotload_server/` — package source
	- `main.py` — CLI entry for launching a server
	- `server.py` — process launcher that spawns the chosen DCC
	- `hooks/` — DCC hook implementations and `BaseHookServer`
		- `base_hook.py` — base class and shared utilities
		- `mayapy.py` — Maya standalone hook
		- `hython.py` — Houdini hython hook
- `sandbox/` — example clients to connect to the server
- `tests/` — unit tests

## Requirements

- Python 3.8+ (uses only standard library features for the server core)
- To run `mayapy` tests or use Maya features you must have a matching Maya
	installation accessible to the repository (mayapy executable).
- To run `hython` features you must have Houdini installed and in the
	locations the hook hints expect.

## Installation (development)

Clone the repo and install in editable mode (optional):

```bash
git clone <repo-url>
cd dcc-hotload-server
poetry install
poetry run dcc-hotload-server --dcc mayapy --version 2024
```

This project is intentionally minimal; additional dependencies are only
required when using DCC-specific functionality.

## Usage

Start a server for a given DCC via the CLI wrapper. Example (Maya):

```bash
python -m dcc_hotload_server.main --dcc mayapy --version 2024
```

Or for Houdini:

```bash
python -m dcc_hotload_server.main --dcc hython --version 19.5
```

The CLI will locate the DCC executable using path hints defined in the
corresponding hook and spawn it in a separate process. That subprocess runs a
small server loop that waits for incoming socket connections and executes the
received Python code.

### Sending commands

See the example clients in `sandbox/` for how to send code to the running
server. The protocol is simple: send a UTF-8 encoded Python script and the
server replies with captured stdout/stderr or error messages.

Special shutdown helper: include the token `__SHUTDOWN__` in the payload to
request the server to stop after processing the current request.

## Hooks and extending

Hooks live in `dcc_hotload_server/hooks`. To add support for another DCC:

1. Implement a subclass of `BaseHookServer`.
2. Provide `hints(self, version)` that returns `SoftwareHint` path hints for
	 different OSes.
3. Implement `initialize()` and `uninitialize()` as needed to prepare the
	 environment (e.g., initialize Maya standalone).

The `server.py` module dynamically imports `dcc_hotload_server.hooks.<dcc>` and
uses the first class that subclasses `BaseHookServer`.

## Testing

Run unit tests with `pytest` from the repository root:

```bash
poetry install --with dev
poetry run pytest tests/
```

Unit tests included exercise core logic but DCC-specific tests require the
corresponding DCC installations available on the host.

## Development notes

- The server serializes the hook instance and starts the real DCC process in a
	new process group so signals can be forwarded/handled appropriately.
- Captured output is returned prefixed with `OUTPUT:` or `ERRORS:` to make
	client parsing straightforward.

## Sandbox clients

Two small example clients are included in `sandbox/`:

- `hython_client.py` — example client targeting the hython server
- `mayapy_client.py` — example client targeting the mayapy server

## Contributing

Contributions welcome — please open issues or pull requests with focused
changes and tests where appropriate.

## License

This repository does not include a license file. Add a license to make your
intentions clear.

