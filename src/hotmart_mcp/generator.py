"""Code generator that reads the Hotmart OpenAPI 3.0.3 spec and produces
async tool modules under ``src/hotmart_mcp/tools/``.

Usage::

    python -m hotmart_mcp.generator
"""

from __future__ import annotations

import json
import re

from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_ROOT = Path(__file__).resolve().parent.parent.parent  # repo root
_SPEC_PATH = _ROOT / "specs" / "hotmart-api.json"
_TOOLS_DIR = Path(__file__).resolve().parent / "tools"

# ---------------------------------------------------------------------------
# Python reserved words that need escaping
# ---------------------------------------------------------------------------

_RESERVED = frozenset({
    "False", "None", "True", "and", "as", "assert", "async", "await",
    "break", "class", "continue", "def", "del", "elif", "else", "except",
    "finally", "for", "from", "global", "if", "import", "in", "is",
    "lambda", "nonlocal", "not", "or", "pass", "raise", "return", "try",
    "while", "with", "yield",
    # builtins commonly shadowed
    "id", "type", "format", "list", "dict", "set", "map", "filter",
    "input", "object", "range", "hash", "help", "max", "min", "next",
    "open", "print", "property", "slice", "sorted", "sum", "super", "zip",
})


def _safe_py_name(name: str) -> str:
    """Append ``_`` if *name* collides with a Python keyword / builtin."""
    return f"{name}_" if name in _RESERVED else name


# ---------------------------------------------------------------------------
# Spec helpers
# ---------------------------------------------------------------------------

def _load_spec() -> dict[str, Any]:
    with open(_SPEC_PATH) as f:
        return json.load(f)


def _resolve_ref(spec: dict[str, Any], ref: str) -> dict[str, Any]:
    """Follow a ``$ref`` pointer like ``#/components/parameters/MaxResults``."""
    parts = ref.lstrip("#/").split("/")
    node: Any = spec
    for p in parts:
        node = node[p]
    return node


def _resolve_schema(spec: dict[str, Any], schema: dict[str, Any]) -> dict[str, Any]:
    """Resolve a schema that may be a ``$ref``."""
    if "$ref" in schema:
        return _resolve_ref(spec, schema["$ref"])
    return schema


def _resolve_param(spec: dict[str, Any], param: dict[str, Any]) -> dict[str, Any]:
    if "$ref" in param:
        return _resolve_ref(spec, param["$ref"])
    return param


def _python_type(schema: dict[str, Any]) -> str:
    """Map an OpenAPI schema to a Python type annotation string."""
    t = schema.get("type", "string")
    if t == "integer":
        return "int"
    if t == "number":
        return "float"
    if t == "boolean":
        return "bool"
    if t == "string":
        return "str"
    if t == "array":
        items_type = _python_type(schema.get("items", {"type": "string"}))
        return f"list[{items_type}]"
    if t == "object":
        return "dict"
    return "str"


def _enum_values(spec: dict[str, Any], schema: dict[str, Any]) -> list[str] | None:
    """Extract enum values from a schema, resolving $ref if needed."""
    resolved = _resolve_schema(spec, schema)
    return resolved.get("enum")


# ---------------------------------------------------------------------------
# Naming helpers
# ---------------------------------------------------------------------------

_METHOD_PREFIX = {
    "get": "get",
    "post": "create",
    "put": "refund",
    "patch": "change",
    "delete": "delete",
}


def _operation_id_to_snake(op_id: str) -> str:
    """Convert camelCase operationId to snake_case."""
    # Insert underscores before uppercase letters
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", op_id)
    return s.lower()


def _derive_func_name(method: str, path: str) -> str:
    """Derive a function name from HTTP method + path when no operationId."""
    parts = [p for p in path.split("/") if p and not p.startswith("{")]
    slug = "_".join(parts[-2:]) if len(parts) >= 2 else "_".join(parts)
    prefix = _METHOD_PREFIX.get(method, method)
    return f"{prefix}_{slug}"


# ---------------------------------------------------------------------------
# Endpoint data model
# ---------------------------------------------------------------------------

class Param:
    def __init__(
        self,
        api_name: str,
        py_name: str,
        py_type: str,
        location: str,  # "path", "query", "body"
        required: bool,
        description: str,
        enum_values: list[str] | None = None,
    ):
        self.api_name = api_name
        self.py_name = py_name
        self.py_type = py_type
        self.location = location
        self.required = required
        self.description = description
        self.enum_values = enum_values


class Endpoint:
    def __init__(
        self,
        func_name: str,
        method: str,
        path: str,
        summary: str,
        description: str,
        params: list[Param],
        tag: str,
    ):
        self.func_name = func_name
        self.method = method
        self.path = path
        self.summary = summary
        self.description = description
        self.params = params
        self.tag = tag


# ---------------------------------------------------------------------------
# Spec parsing
# ---------------------------------------------------------------------------

def _parse_endpoints(spec: dict[str, Any]) -> list[Endpoint]:
    endpoints: list[Endpoint] = []

    for path, path_item in spec.get("paths", {}).items():
        for method in ("get", "post", "put", "patch", "delete"):
            if method not in path_item:
                continue
            op = path_item[method]

            # --- function name ---
            op_id = op.get("operationId")
            if op_id:
                func_name = _operation_id_to_snake(op_id)
            else:
                func_name = _derive_func_name(method, path)

            # --- tag ---
            tag = (op.get("tags") or ["misc"])[0]

            # --- params (path + query) ---
            params: list[Param] = []
            for raw_p in op.get("parameters", []):
                p = _resolve_param(spec, raw_p)
                schema = p.get("schema", {})
                resolved_schema = _resolve_schema(spec, schema)
                py_type = _python_type(resolved_schema)
                enums = _enum_values(spec, schema)
                desc = p.get("description", "")
                if enums:
                    desc += f". Values: {', '.join(str(v) for v in enums)}"
                params.append(Param(
                    api_name=p["name"],
                    py_name=_safe_py_name(p["name"]),
                    py_type=py_type,
                    location=p["in"],
                    required=p.get("required", False),
                    description=desc,
                    enum_values=enums,
                ))

            # --- body params ---
            request_body = op.get("requestBody")
            if request_body:
                content = request_body.get("content", {})
                json_schema = content.get("application/json", {}).get("schema", {})
                resolved_body = _resolve_schema(spec, json_schema)
                body_required_fields = set(resolved_body.get("required", []))
                for prop_name, prop_schema in resolved_body.get("properties", {}).items():
                    resolved_prop = _resolve_schema(spec, prop_schema)
                    py_type = _python_type(resolved_prop)
                    enums = _enum_values(spec, prop_schema)
                    desc = resolved_prop.get("description", prop_schema.get("description", ""))
                    if enums:
                        desc += f". Values: {', '.join(str(v) for v in enums)}"
                    params.append(Param(
                        api_name=prop_name,
                        py_name=_safe_py_name(prop_name),
                        py_type=py_type,
                        location="body",
                        required=prop_name in body_required_fields,
                        description=desc,
                        enum_values=enums,
                    ))

            endpoints.append(Endpoint(
                func_name=func_name,
                method=method,
                path=path,
                summary=op.get("summary", ""),
                description=op.get("description", ""),
                params=params,
                tag=tag,
            ))

    return endpoints


# ---------------------------------------------------------------------------
# Code generation
# ---------------------------------------------------------------------------

def _gen_function(ep: Endpoint) -> str:
    """Generate a single async function string for an endpoint."""

    # Separate params by kind
    path_params = [p for p in ep.params if p.location == "path"]
    query_params = [p for p in ep.params if p.location == "query"]
    body_params = [p for p in ep.params if p.location == "body"]

    has_query = bool(query_params)
    has_body = bool(body_params)

    # --- signature ---
    required_args = [p for p in ep.params if p.required]
    optional_args = [p for p in ep.params if not p.required]

    sig_parts: list[str] = []
    for p in required_args:
        sig_parts.append(f"{p.py_name}: {p.py_type}")
    for p in optional_args:
        sig_parts.append(f"{p.py_name}: Optional[{p.py_type}] = None")

    sig_str = ",\n    ".join(sig_parts)
    if sig_parts:
        sig_str = f"\n    {sig_str},\n"

    # --- docstring ---
    doc_lines = [ep.summary]
    if ep.description and ep.description != ep.summary:
        doc_lines.append("")
        doc_lines.append(ep.description)

    # param docs
    any_param = required_args + optional_args
    if any_param:
        doc_lines.append("")
        doc_lines.append("Args:")
        for p in any_param:
            desc = p.description or p.api_name
            doc_lines.append(f"    {p.py_name}: {desc}")

    docstring = "\n    ".join(doc_lines)

    # --- body ---
    body_lines: list[str] = []

    # Build path string
    # Check if path has {param} placeholders
    fmt_path = ep.path
    for pp in path_params:
        fmt_path = fmt_path.replace(f"{{{pp.api_name}}}", f"{{{pp.py_name}}}")

    has_path_params = bool(path_params)
    if has_path_params:
        body_lines.append(f'endpoint = f"{fmt_path}"')
    else:
        body_lines.append(f'endpoint = "{ep.path}"')

    # Build query params dict
    if has_query:
        body_lines.append("params = {}")
        for p in query_params:
            body_lines.append(f"if {p.py_name} is not None:")
            if p.py_name != p.api_name:
                body_lines.append(f'    params["{p.api_name}"] = {p.py_name}')
            else:
                body_lines.append(f'    params["{p.api_name}"] = {p.py_name}')

    # Build body dict
    if has_body:
        body_lines.append("body = {}")
        for p in body_params:
            if p.required:
                body_lines.append(f'body["{p.api_name}"] = {p.py_name}')
            else:
                body_lines.append(f"if {p.py_name} is not None:")
                body_lines.append(f'    body["{p.api_name}"] = {p.py_name}')

    # API call
    method = ep.method
    if method == "get":
        params_arg = "params=params" if has_query else ""
        body_lines.append(f"result = await get_client().get(endpoint{', ' + params_arg if params_arg else ''})")
    elif method == "post":
        args = []
        if has_body:
            args.append("json=body")
        if has_query:
            args.append("params=params")
        args_str = ", ".join(args)
        body_lines.append(f"result = await get_client().post(endpoint{', ' + args_str if args_str else ''})")
    elif method == "put":
        args = []
        if has_body:
            args.append("json=body")
        if has_query:
            args.append("params=params")
        args_str = ", ".join(args)
        body_lines.append(f"result = await get_client().put(endpoint{', ' + args_str if args_str else ''})")
    elif method == "patch":
        args = []
        if has_body:
            args.append("json=body")
        if has_query:
            args.append("params=params")
        args_str = ", ".join(args)
        body_lines.append(f"result = await get_client().patch(endpoint{', ' + args_str if args_str else ''})")
    elif method == "delete":
        params_arg = "params=params" if has_query else ""
        body_lines.append(f"result = await get_client().delete(endpoint{', ' + params_arg if params_arg else ''})")

    body_lines.append('return json.dumps(result, indent=2)')

    body_str = "\n    ".join(body_lines)

    return f'''async def {ep.func_name}({sig_str}) -> str:
    """{docstring}"""
    {body_str}'''


def _gen_module(tag: str, endpoints: list[Endpoint]) -> str:
    """Generate a complete module file for a tag group."""
    module_name = tag.lower()
    func_strs = [_gen_function(ep) for ep in endpoints]
    funcs_code = "\n\n\n".join(func_strs)

    # Build __all__
    all_names = [f'"{ep.func_name}"' for ep in endpoints]
    all_str = ", ".join(all_names)

    return f'''"""Auto-generated Hotmart API tools — {module_name}."""

import json
from typing import Optional

from hotmart_mcp._shared import get_client

__all__ = [{all_str}]


{funcs_code}
'''


def _gen_init(tags: list[str]) -> str:
    """Generate ``tools/__init__.py`` that re-exports all tool functions."""
    imports = "\n".join(f"from .{tag.lower()} import *  # noqa: F401,F403" for tag in sorted(tags))
    return f'''"""Auto-generated: re-exports all tool functions."""

{imports}
'''


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    spec = _load_spec()
    all_endpoints = _parse_endpoints(spec)

    # Group by tag
    groups: dict[str, list[Endpoint]] = {}
    for ep in all_endpoints:
        groups.setdefault(ep.tag, []).append(ep)

    _TOOLS_DIR.mkdir(parents=True, exist_ok=True)

    total_funcs = 0
    print(f"Generating tools from {_SPEC_PATH.name}...")
    print()

    for tag, endpoints in sorted(groups.items()):
        module_name = tag.lower()
        code = _gen_module(tag, endpoints)
        out_path = _TOOLS_DIR / f"{module_name}.py"
        out_path.write_text(code, encoding="utf-8")
        count = len(endpoints)
        total_funcs += count
        func_names = ", ".join(ep.func_name for ep in endpoints)
        print(f"  {module_name}.py — {count} functions: {func_names}")

    # __init__.py
    init_code = _gen_init(list(groups.keys()))
    (_TOOLS_DIR / "__init__.py").write_text(init_code, encoding="utf-8")

    print()
    print(f"Done: {len(groups)} modules, {total_funcs} total functions.")


if __name__ == "__main__":
    main()
