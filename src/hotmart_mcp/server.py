"""Hotmart MCP Server — FastMCP entry point."""

import importlib
import inspect
import os
import pkgutil
from asyncio import iscoroutinefunction

from fastmcp import FastMCP

from hotmart_mcp import tools as tools_pkg
from hotmart_mcp import apps as apps_pkg

INSTRUCTIONS = (
    "Hotmart API server providing tools for managing sales, subscriptions, "
    "club (members area), products, coupons, support tickets, and negotiation. "
    "Use the available tools to query and operate on Hotmart resources. "
    "Apps with name ending in `_app` return interactive UI (charts, DataTables) "
    "and only render in clients that support Prefab UI (e.g. Claude Desktop)."
)

mcp = FastMCP("hotmart", instructions=INSTRUCTIONS)


def _discover_and_register_tools() -> int:
    """Import all modules under hotmart_mcp.tools and register async functions."""
    registered = 0
    for module_info in pkgutil.iter_modules(tools_pkg.__path__, prefix=f"{tools_pkg.__name__}."):
        if module_info.name.endswith("__init__"):
            continue
        module = importlib.import_module(module_info.name)
        for name, obj in inspect.getmembers(module, iscoroutinefunction):
            if name.startswith("_"):
                continue
            mcp.tool()(obj)
            registered += 1
    return registered


def _discover_and_register_apps() -> int:
    """Import all modules under hotmart_mcp.apps and register apps (app=True)."""
    registered = 0
    for module_info in pkgutil.iter_modules(apps_pkg.__path__, prefix=f"{apps_pkg.__name__}."):
        if module_info.name.endswith("__init__"):
            continue
        module = importlib.import_module(module_info.name)
        for name, obj in inspect.getmembers(module, iscoroutinefunction):
            if name.startswith("_") or not name.endswith("_app"):
                continue
            mcp.tool(app=True)(obj)
            registered += 1
    return registered


def _apply_code_mode() -> None:
    """Apply Code Mode transform to collapse tools into 3 meta-tools.

    OPT-IN — desabilitado por default porque o CodeMode colapsa TODAS as
    tools (incluindo apps com app=True) em apenas `search`+`get_schema`+
    `execute`, o que quebra a renderização Prefab UI no Claude Desktop.
    Apps só rendererizam como UI nativa se forem expostas como tools
    individuais ao cliente.

    Ative via `HOTMART_MCP_CODE_MODE=1` se quiser collapse (útil pra
    clientes que NÃO usam Desktop e querem economia de context window
    com 40 entries — sacrifica os apps interativos).
    """
    if os.environ.get("HOTMART_MCP_CODE_MODE", "").lower() not in ("1", "true", "yes"):
        return
    try:
        from fastmcp.experimental.transforms.code_mode import CodeMode
        mcp.add_transform(CodeMode())
        print("hotmart-mcp: CodeMode active (collapses 40 entries to 3 meta-tools — apps not rendered)")
    except ImportError:
        pass  # Code Mode not available in this fastmcp version


def main() -> None:
    """CLI entry point for the Hotmart MCP server."""
    tools_count = _discover_and_register_tools()
    apps_count = _discover_and_register_apps()
    _apply_code_mode()
    print(f"hotmart-mcp: {tools_count} tool(s) + {apps_count} app(s) registered, starting server...")
    mcp.run()


if __name__ == "__main__":
    main()
