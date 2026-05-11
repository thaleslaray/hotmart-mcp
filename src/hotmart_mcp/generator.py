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


_DATE_NAME_HINTS = ("date", "_at", "timestamp")
_DATE_EXAMPLE_HINT = (
    "Unix timestamp in **milliseconds** (not seconds, not ISO). "
    "Ex: `1730419200000` = 2024-11-01 00:00 UTC. "
    "Python: `int(datetime(2024,11,1).timestamp() * 1000)`."
)


# PT-BR -> EN substitutions for common param descriptions (F3: EN only).
_PT_TO_EN: list[tuple[str, str]] = [
    ("Número máximo de resultados por página", "Max results per page"),
    ("Token de paginação para a próxima página", "Pagination token for the next page"),
    ("ID do produto", "Product ID"),
    ("Data inicial", "Start date"),
    ("Data final", "End date"),
    ("Data de início de validade", "Validity start date"),
    ("Data de início", "Start date"),
    ("Origem da venda", "Sale source"),
    ("Código da transação", "Transaction code"),
    ("Seleção de campos customizados na resposta", "Custom field selection in response"),
    ("Nome do comprador", "Buyer name"),
    ("E-mail do comprador", "Buyer email"),
    ("Código da oferta", "Offer code"),
    ("Papel de comissão do usuário autenticado", "Authenticated user's commission role"),
    ("Status da transação", "Transaction status"),
    ("Tipo de pagamento", "Payment type"),
    ("Código do assinante", "Subscriber code"),
    ("Status da assinatura", "Subscription status"),
    ("Subdomínio da área de membros", "Members area subdomain (the slug from `hotmart.com/club/<slug>` URL)"),
    ("ID do módulo", "Module ID"),
    ("ID do usuário", "User ID"),
    ("ID do evento", "Event ID"),
    ("Chave da oferta", "Offer key"),
    ("E-mail", "Email"),
    ("Data de adesão inicial", "Subscription start date (lower bound)"),
    ("Data de adesão final", "Subscription start date (upper bound)"),
    ("Data de adesão", "Subscription accession date"),
    ("Percentual de desconto (entre 0 e 0.99, exclusivo)", "Discount fraction (between 0 and 0.99 exclusive)"),
    ("Percentual de desconto", "Discount fraction"),
    ("CPF ou CNPJ do assinante (obrigatório para BOLETO)", "Subscriber's CPF or CNPJ (required when payment_method is BILLET)"),
    ("CPF ou CNPJ do assinante", "Subscriber's CPF or CNPJ"),
    ("Lista de códigos de assinante", "List of subscriber codes"),
    ("Códigos de assinante", "Subscriber codes"),
    ("Código do cupom", "Coupon code"),
    ("ID do cupom", "Coupon ID"),
    ("Quantidade de parcelas", "Number of installments"),
    ("Dia de vencimento", "Due day (1-31)"),
    ("(timestamp em milissegundos desde epoch)", ""),
    ("(timestamp em milissegundos)", ""),
    ("(timestamp ms)", ""),
]


def _translate_pt(desc: str) -> str:
    """Apply known PT-BR -> EN replacements in param descriptions (F3)."""
    for pt, en in _PT_TO_EN:
        desc = desc.replace(pt, en)
    return desc.strip(" .,").strip()


_DISCOUNT_HINT = (
    "**Fraction between 0 and 1** (NOT percent). "
    "Ex: `0.25` = 25% off. Pass `0.10` for 10%, NOT `10`."
)
_BILLET_NOTE = "Note: API uses English `'BILLET'` (NOT Portuguese `'BOLETO'`)."

_DISCOUNT_PARAM_NAMES = {"discount", "pct", "percentage", "commission_pct", "rate"}


def _enrich_param_description(
    api_name: str,
    base_desc: str,
    resolved_schema: dict[str, Any],
    enum_values: list[str] | None,
) -> str:
    """Format hints for params — kept compact and in EN.

    SEP-1382 separates tool description (what/when) from parameter description
    (format/validation). This goes into the Args: block, which FastMCP maps to
    inputSchema.properties[].description.
    """
    desc = _translate_pt(base_desc.strip()) if base_desc else api_name
    name_lower = api_name.lower()

    # --- date timestamps (ms) ---
    # Relaxed: trigger on name match + (int64 OR plain integer OR "ms" in desc).
    # Some Hotmart endpoints omit `format: int64` for date fields (e.g. accession_date).
    is_date_name = any(h in name_lower for h in _DATE_NAME_HINTS)
    schema_type = resolved_schema.get("type")
    is_integer = schema_type == "integer"
    has_ms_hint = "ms" in desc.lower() or "milissegundos" in desc.lower() or "millisecond" in desc.lower()
    if is_date_name and (is_integer or has_ms_hint):
        desc += f". {_DATE_EXAMPLE_HINT}"

    # --- discount / percentage as fraction ---
    if name_lower in _DISCOUNT_PARAM_NAMES:
        desc += f". {_DISCOUNT_HINT}"

    # --- batch arrays (lists of codes/IDs) ---
    if schema_type == "array":
        items = resolved_schema.get("items", {})
        items_type = items.get("type", "string")
        if items_type == "string":
            desc += ". Pass a JSON array of strings, e.g. `['ABC123XY', 'DEF456ZW']`."
        elif items_type == "integer":
            desc += ". Pass a JSON array of integers, e.g. `[12345, 67890]`."

    # --- enums: inline if <=3 values, bullet list if more (case-sensitive warning) ---
    if enum_values:
        if len(enum_values) <= 3:
            desc += f". Allowed values: {', '.join(repr(v) for v in enum_values)}"
        else:
            desc += ".\n        Allowed values (case-sensitive, pass EXACTLY as listed):"
            for v in enum_values:
                desc += f"\n          - `{v}`"
        # Flag BILLET/BOLETO confusion explicitly
        if "BILLET" in (enum_values or []):
            desc += f"\n        {_BILLET_NOTE}"

    # --- code/id formats ---
    fmt = resolved_schema.get("format")
    if fmt == "uuid":
        desc += ". Format: UUID (ex: `550e8400-e29b-41d4-a716-446655440000`)"
    elif api_name.endswith("_code") and resolved_schema.get("type") == "string":
        desc += ". Format: alphanumeric Hotmart code (ex: `H123A4B5`, not UUID, not int)"

    return desc


# Alias for backwards compat
_enrich_description = _enrich_param_description


# ---------------------------------------------------------------------------
# Tool-level description (SEP-1382: separate from param descriptions)
# ---------------------------------------------------------------------------

# Canonical verbs per HTTP method × intent (BFCL-aligned vocabulary)
_VERB_REMAP = {
    # generic remaps for clearer routing
    "get": "get",        # detail/singular
    "list": "list",      # collection
    "create": "create",
    "update": "update",
    "patch": "update",
    "delete": "delete",
    "cancel": "cancel",
    "reactivate": "reactivate",
    "refund": "refund",
    "change": "update",  # change_subscription_due_day -> subscription_update
    "generate": "generate",
}


def _canonical_func_name(op_id: str | None, method: str, path: str, tag: str) -> str:
    """Build hotmart_{resource}_{verb} name (F4: namespacing + verb taxonomy).

    Anthropic + BFCL converge on: prefix with service, lock verb vocabulary,
    put resource before verb (read better in tool lists).
    """
    if op_id:
        base = _operation_id_to_snake(op_id)
    else:
        base = _derive_func_name(method, path)

    # split into tokens
    tokens = base.split("_")

    # find verb (first known verb token)
    verb = None
    rest: list[str] = []
    for t in tokens:
        if verb is None and t in _VERB_REMAP:
            verb = _VERB_REMAP[t]
        else:
            rest.append(t)

    # fallback verb from HTTP method
    if verb is None:
        verb = _VERB_REMAP.get(method, method)

    resource = "_".join(rest) if rest else tag.lower()

    # F4 verb taxonomy: collection → `list`, singular → `get`.
    # Heuristic: if HTTP method is GET and the resource (or its last token) is plural,
    # promote `get` → `list`. Also: "history", "summary", "participants", "commissions",
    # "details", "transactions", "purchases", "pages", "offers", "plans", "modules",
    # "students", "coupons" are collection-y nouns.
    _COLLECTION_TOKENS = {
        "history", "summary", "participants", "commissions", "details",
        "transactions", "purchases", "pages", "offers", "plans", "modules",
        "students", "coupons",
    }
    if verb == "get" and method == "get":
        last = resource.split("_")[-1] if resource else ""
        is_plural = last.endswith("s") and not last.endswith("ss") and last not in {"status"}
        is_collection_noun = last in _COLLECTION_TOKENS or any(
            t in _COLLECTION_TOKENS for t in resource.split("_")
        )
        # but singular like "event_info", "subscriber_purchases" with path param → keep get
        # Heuristic: if no path param in op (only query/none), it's a list endpoint.
        # We can't see params here — use the plural test only.
        if is_plural or is_collection_noun:
            verb = "list"

    return f"hotmart_{resource}_{verb}"


# Pairs of tools that are semantically close — generate when-NOT hints (F7).
# Maps tool_name -> "use OTHER_TOOL when you want X instead"
_DISAMBIGUATION: dict[str, str] = {
    "hotmart_sales_history_list":
        "Don't use this for aggregated metrics — use `hotmart_sales_summary_list` for totals/counts.",
    "hotmart_sales_summary_list":
        "Don't use this for per-transaction details — use `hotmart_sales_history_list` for the raw list.",
    "hotmart_subscriptions_list":
        "Don't use this for payment events — use `hotmart_subscription_transactions_list` for charges/refunds per subscription.",
    "hotmart_subscription_transactions_list":
        "Don't use this for the subscription list itself — use `hotmart_subscriptions_list`.",
    "hotmart_subscription_cancel":
        "Use this for ONE subscriber_code. For 2+ subscriptions, use `hotmart_batch_subscriptions_cancel`.",
    "hotmart_batch_subscriptions_cancel":
        "Use this for multiple subscriber_codes at once. For a single one, prefer `hotmart_subscription_cancel`.",
    "hotmart_subscription_reactivate":
        "Use this for ONE subscriber_code. For 2+, use `hotmart_batch_subscriptions_reactivate`.",
    "hotmart_batch_subscriptions_reactivate":
        "Use this for multiple subscriber_codes at once. For a single one, prefer `hotmart_subscription_reactivate`.",
    "hotmart_modules_list":
        "Lists module containers only. To get pages inside a module, use `hotmart_module_pages_list` with the module_id.",
    "hotmart_module_pages_list":
        "Requires module_id from `hotmart_modules_list` first.",
}


def _build_tool_description(
    func_name: str,
    summary: str,
    description: str,
    example_args: str,
) -> str:
    """Build a 4-line tool description following SOTA (F1+F5+F6+F7).

    Format:
        {VERB} {RESOURCE} in Hotmart. {WHEN to use}.
        Returns: {key fields}.
        Example: tool_name({param: value}).
        [optional] {WHEN NOT to use, cross-ref to similar tool}.

    Target: 40-80 tokens (F5). EN only (F3). Verb front-loaded (F1).
    """
    # First line — prefer summary (concise), fallback to description first sentence
    main = (summary or description or func_name).strip()
    # Take only first sentence if summary is long
    if "." in main and len(main) > 100:
        main = main.split(".")[0].strip() + "."
    if not main.endswith("."):
        main += "."

    lines = [main]

    if example_args:
        lines.append(f"Example: {func_name}({example_args}).")

    # Cross-ref disambiguation
    when_not = _DISAMBIGUATION.get(func_name)
    if when_not:
        lines.append(when_not)

    return " ".join(lines)


def _build_example_args(params: list["Param"]) -> str:
    """Build a tiny example args string for the description.

    Uses required path params (often the most discriminating) + 1 optional filter.
    """
    parts: list[str] = []
    seen_keys: set[str] = set()
    for p in params:
        if p.location == "path" and p.py_name not in seen_keys:
            example_val = _example_value_for(p)
            parts.append(f"{p.py_name}={example_val}")
            seen_keys.add(p.py_name)
    # add one optional filter if available (max_results or first enum)
    if not parts or len(parts) < 2:
        for p in params:
            if not p.required and p.py_name not in seen_keys:
                if p.py_name in ("max_results", "transaction_status", "status") and p.enum_values:
                    parts.append(f"{p.py_name}={p.enum_values[0]!r}")
                elif p.py_name == "max_results":
                    parts.append("max_results=10")
                else:
                    continue
                seen_keys.add(p.py_name)
                break
    return ", ".join(parts[:2])


def _example_value_for(p: "Param") -> str:
    """Generate a small example literal for a parameter."""
    if p.py_type == "int":
        return "12345"
    if p.api_name.endswith("_code"):
        return "'ABC123XY'"
    if p.api_name in ("subdomain",):
        return "'my-club-slug'"
    if p.enum_values:
        return repr(p.enum_values[0])
    return "'…'"


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

            # --- tag (resolve first — used in canonical naming fallback) ---
            tag = (op.get("tags") or ["misc"])[0]

            # --- function name (canonical: hotmart_{resource}_{verb}) ---
            op_id = op.get("operationId")
            func_name = _canonical_func_name(op_id, method, path, tag)

            # --- params (path + query) ---
            params: list[Param] = []
            for raw_p in op.get("parameters", []):
                p = _resolve_param(spec, raw_p)
                schema = p.get("schema", {})
                resolved_schema = _resolve_schema(spec, schema)
                py_type = _python_type(resolved_schema)
                enums = _enum_values(spec, schema)
                desc = _enrich_description(p["name"], p.get("description", ""), resolved_schema, enums)
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
                    raw_desc = resolved_prop.get("description", prop_schema.get("description", ""))
                    desc = _enrich_description(prop_name, raw_desc, resolved_prop, enums)
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
    # Compact tool-level description (SEP-1382: separate from param descriptions).
    # F1 front-loaded verb, F3 EN-only, F5 ~40-80 tokens, F6 inline example, F7 disambig.
    example_args = _build_example_args(ep.params)
    tool_desc = _build_tool_description(
        func_name=ep.func_name,
        summary=ep.summary,
        description=ep.description,
        example_args=example_args,
    )
    doc_lines = [tool_desc]

    # param docs (these map to inputSchema.properties[].description via FastMCP)
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
