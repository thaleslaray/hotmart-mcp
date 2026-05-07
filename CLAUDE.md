# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

FastMCP server exposing the Hotmart API (sales, subscriptions, club/members area, products, coupons, support tickets, negotiation). Tool functions are **code-generated** from `specs/hotmart-api.json` (OpenAPI 3.0.3) — do not hand-edit files in `src/hotmart_mcp/tools/`.

## Common commands

```bash
# Install (editable) — creates the `hotmart-mcp` console script
uv pip install -e .   # or: pip install -e .

# Regenerate tool modules from the OpenAPI spec
python -m hotmart_mcp.generator

# Run the MCP server (stdio)
hotmart-mcp
# or
python -m hotmart_mcp.server
```

No test suite, linter, or formatter is configured.

## Required environment

The client reads three env vars at first use (raises `KeyError` if missing):

- `HOTMART_CLIENT_ID`
- `HOTMART_CLIENT_SECRET`
- `HOTMART_BASIC_AUTH` (base64 of `client_id:client_secret`, used for the OAuth token request)

A local `src/hotmart_mcp/.env` exists for development; it's not auto-loaded by the code — load it via the MCP client config or shell.

## Architecture

**Three-layer structure**, each with a distinct responsibility:

1. `client.py` — `HotmartClient`, an `httpx.AsyncClient` wrapper. Handles OAuth2 client-credentials token caching (`_ensure_token`, lock-protected, refreshed at 80% of `expires_in`), automatic 401-retry-once after invalidating the token, 429 backoff with `Retry-After`, and `get_all_pages` cursor pagination using `page_info.next_page_token` / `items` keys. Exposes `ApiError` / `AuthError` / `RateLimitError`.

2. `_shared.py` — Lazy module-level singleton (`get_client()`). All tool functions call this; the client is constructed on first use so `import hotmart_mcp.tools.*` does not require env vars to be set.

3. `tools/*.py` — One module per OpenAPI tag (`sales`, `subscriptions`, `club`, `products`, `coupons`, `tickets`, `negotiation`). Every public async function = one MCP tool, returns `json.dumps(...)`. `__all__` lists exported functions per module.

`server.py` is the entry point: `_discover_and_register_tools()` walks `hotmart_mcp.tools` with `pkgutil.iter_modules`, imports each module, and registers every public coroutine via `mcp.tool()`. `_apply_code_mode()` optionally collapses tools into 3 meta-tools if `fastmcp.server.code_mode.CodeMode` is available — this is why the `hotmart` MCP exposes `search` / `get_schema` / `execute` instead of the raw tools when Code Mode is active.

## Code generation flow

`generator.py` reads `specs/hotmart-api.json`, groups endpoints by OpenAPI `tags[0]`, and writes one file per tag into `tools/`:

- Function naming: derived from `operationId` (or method+path fallback) — see `_operation_id_to_snake` and `_derive_func_name`.
- Parameter names: passed through `_safe_py_name` to suffix `_` on Python keywords / common builtins (e.g. `id` → `id_`, `format` → `format_`).
- Type mapping: `_python_type` translates OpenAPI types/enums to `Optional[...]` annotations; enum values are listed in the docstring.
- Body params: serialised via `json=...`; query params via `params=...`; path params interpolated into the endpoint string.

When the upstream spec changes, **regenerate** rather than edit `tools/*.py`. The `__init__.py` in `tools/` is also generated.

## Adding behaviour

- New custom tools (not in the spec): create a new module under `tools/` with public async functions. The discovery loop in `server.py` will pick them up automatically — no manual registration. Avoid clashing with module names the generator owns or your file will be overwritten on next regen.
- Cross-cutting client changes (auth, retries, pagination): edit `client.py`. All generated tools call `get_client()` and reuse the same instance.
