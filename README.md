# hotmart-mcp

Hotmart API MCP server — 28 tools auto-generated from the official Hotmart OpenAPI 3.0.3 spec, exposed via [FastMCP](https://github.com/jlowin/fastmcp). Optional Code Mode collapses everything into 3 meta-tools (`search`, `get_schema`, `execute`) when available.

## What is this?

An MCP server that wraps the public Hotmart Developer API (`developers.hotmart.com`) so Claude or any MCP client can manage sales, subscriptions, club (members area), products, coupons, support tickets, and negotiation flows.

The tool functions are **generated** from `specs/hotmart-api.json` by `hotmart_mcp.generator` — modules under `src/hotmart_mcp/tools/` are not hand-edited.

## Setup

```bash
# Install
pip install -e ".[dev]"

# Required (OAuth2 client credentials from Hotmart Developer Portal)
export HOTMART_CLIENT_ID="..."
export HOTMART_CLIENT_SECRET="..."
export HOTMART_BASIC_AUTH="..."   # base64(client_id:client_secret)

# Run
hotmart-mcp
```

## Usage with Claude Code

Add to your `.mcp.json`:

```json
{
  "mcpServers": {
    "hotmart": {
      "command": "hotmart-mcp",
      "env": {
        "HOTMART_CLIENT_ID": "your_client_id",
        "HOTMART_CLIENT_SECRET": "your_client_secret",
        "HOTMART_BASIC_AUTH": "base64(client_id:client_secret)"
      }
    }
  }
}
```

## Architecture

```
specs/hotmart-api.json (OpenAPI 3.0.3)
    | generator.py groups by tag
Python async tool functions (7 modules, 28 tools)
    | server.py auto-discovers via pkgutil + registers
FastMCP server
    | optional CodeMode transform
3 meta-tools (search, get_schema, execute) when Code Mode available
    | agent uses
Claude / any MCP client
```

### Client stack (`client.py`)

```
Request flow:
  1. _ensure_token — OAuth2 client_credentials, cached at 80% of expires_in, lock-protected
  2. _request — issues HTTP via shared httpx.AsyncClient
  3. 401 once → invalidate token, retry
  4. 429 → respects Retry-After + exponential backoff (MAX_RETRIES=3)
  5. _raise_for_status → typed errors (ApiError / AuthError / RateLimitError)

Pagination helper:
  get_all_pages — follows page_info.next_page_token, accumulates items
```

## Covered Endpoints

| Module | Tools | Description |
|--------|-------|-------------|
| sales | 6 | History, summary, participants, commissions, price details, refund |
| subscriptions | 9 | List, summary, transactions, cancel/reactivate (single + batch), change due day |
| club | 4 | Members area: students, modules, module pages, student progress |
| products | 3 | Product list, offers, plans |
| coupons | 3 | List, create, delete |
| tickets | 2 | Event info, event participants |
| negotiation | 1 | Generate negotiation link |

**Total: 28 auto-generated tools.**

## Maintenance

### Regenerate tools from the spec

When the upstream OpenAPI spec changes (replace `specs/hotmart-api.json`):

```bash
bash scripts/regenerate.sh
```

This runs `python -m hotmart_mcp.generator`, which rewrites every file under `src/hotmart_mcp/tools/` (including `__init__.py`). Do not hand-edit those files — changes are lost on the next regen.

### Adding custom (non-spec) tools

Drop a new module under `src/hotmart_mcp/tools/` with public async functions. `server.py:_discover_and_register_tools` picks them up automatically via `pkgutil.iter_modules`. Avoid module names the generator owns (`sales`, `subscriptions`, `club`, `products`, `coupons`, `tickets`, `negotiation`) or they'll be overwritten.

## License

MIT
