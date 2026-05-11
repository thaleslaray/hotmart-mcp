#!/usr/bin/env python3
"""End-to-end test of the 19 GET tools.

Strategy:
  1. Load .env credentials
  2. Run "root" tools (no path params) → extract IDs
  3. Run "leaf" tools (need path params) with discovered IDs
  4. Capture: latency, status, error type, response shape per call

Output: scripts/test-results.json + console summary table.

Usage:
    PYTHONPATH=src python3 scripts/test_all_gets.py
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
import time
import traceback
from pathlib import Path


def load_dotenv():
    env_path = Path(__file__).resolve().parent.parent / "src" / "hotmart_mcp" / ".env"
    if not env_path.exists():
        print(f"❌ .env not found: {env_path}", file=sys.stderr)
        sys.exit(2)
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


async def safe_call(name, coro):
    """Run a tool, capture timing + first-line error if any."""
    t0 = time.time()
    try:
        result_str = await coro
        try:
            data = json.loads(result_str)
        except Exception:
            data = {"_raw": result_str[:500]}
        return {
            "tool": name,
            "ok": True,
            "duration_ms": int((time.time() - t0) * 1000),
            "shape": _describe_shape(data),
            "sample": _sample_first(data),
        }
    except Exception as e:
        return {
            "tool": name,
            "ok": False,
            "duration_ms": int((time.time() - t0) * 1000),
            "error_type": type(e).__name__,
            "error_msg": str(e)[:300],
            "traceback": traceback.format_exc().splitlines()[-3:],
        }


def _describe_shape(data):
    if isinstance(data, dict):
        keys = list(data.keys())[:8]
        items = data.get("items")
        if isinstance(items, list):
            return f"dict(keys={keys}, items_count={len(items)})"
        return f"dict(keys={keys})"
    if isinstance(data, list):
        return f"list(len={len(data)})"
    return type(data).__name__


def _sample_first(data):
    if isinstance(data, dict):
        items = data.get("items")
        if isinstance(items, list) and items:
            first = items[0]
            if isinstance(first, dict):
                return {k: v for k, v in list(first.items())[:5]}
        return {k: v for k, v in list(data.items())[:3]}
    if isinstance(data, list) and data:
        return data[0]
    return None


def _extract_id(result, *paths):
    """Walk extracted sample looking for first non-empty value at any path."""
    if not result.get("ok"):
        return None
    sample = result.get("sample")
    if not isinstance(sample, dict):
        return None
    for path in paths:
        keys = path.split(".")
        cur = sample
        for k in keys:
            if isinstance(cur, dict) and k in cur:
                cur = cur[k]
            else:
                cur = None
                break
        if cur not in (None, "", []):
            return cur
    return None


async def main():
    load_dotenv()

    from hotmart_mcp.tools import sales, subscriptions, club, products, tickets, coupons

    results = []
    ids = {}

    # ── Wave 1: root tools (no path params) ──
    print("═══ WAVE 1 — root tools ═══")
    root_calls = [
        ("get_sales_history", sales.hotmart_sales_history_list(max_results=5)),
        ("get_sales_summary", sales.hotmart_sales_summary_list(max_results=5)),
        ("get_sales_participants", sales.hotmart_sales_participants_list(max_results=5)),
        ("get_sales_commissions", sales.hotmart_sales_commissions_list(max_results=5)),
        ("get_sales_price_details", sales.hotmart_sales_price_details_list(max_results=5)),
        ("get_subscriptions", subscriptions.hotmart_subscriptions_list(max_results=5)),
        ("get_subscriptions_summary", subscriptions.hotmart_subscriptions_summary_list(max_results=5)),
        ("get_subscription_transactions", subscriptions.hotmart_subscription_transactions_list(max_results=5)),
        ("list_products", products.hotmart_products_list(max_results=5)),
    ]
    for name, coro in root_calls:
        r = await safe_call(name, coro)
        results.append(r)
        flag = "✅" if r["ok"] else "❌"
        print(f"  {flag} {name:35s} {r['duration_ms']:>5}ms  {r.get('error_msg', r.get('shape',''))[:80]}")

    # ── Discover IDs ──
    def find(tool_name):
        for r in results:
            if r["tool"] == tool_name:
                return r
        return None

    # subscriber_code: from get_subscriptions
    r = find("get_subscriptions")
    ids["subscriber_code"] = _extract_id(r, "subscriber.code", "subscriber_code", "code")

    # product_id: from list_products
    r = find("list_products")
    ids["product_id"] = _extract_id(r, "id", "product_id")
    # module_id and user_id discovered later (after wave 2 club calls)
    ids["module_id"] = None
    ids["user_id"] = None

    # transaction_code: from get_sales_history (for refund — but we won't call)
    r = find("get_sales_history")
    ids["transaction"] = _extract_id(r, "purchase.transaction", "transaction")

    print()
    print("Discovered IDs:")
    for k, v in ids.items():
        print(f"  {k} = {v!r}")
    print()

    # ── Wave 2: tools with path params ──
    print("═══ WAVE 2 — tools with path params ═══")
    sub_code = ids.get("subscriber_code")
    mod_id = ids.get("module_id")
    user_id = ids.get("user_id")
    prod_id = ids.get("product_id")

    # Try to discover subdomain from products response
    r_prod = find("list_products")
    subdomain = None
    if r_prod and r_prod.get("ok"):
        # Look in raw response for members area / subdomain hints
        raw = json.dumps(r_prod.get("sample") or {})
        import re as _re
        m = _re.search(r"https?://([a-z0-9-]+)\.club\.hotmart\.com", raw)
        if m:
            subdomain = m.group(1)
        else:
            # also check other key naming conventions
            sample = r_prod.get("sample") or {}
            subdomain = sample.get("subdomain") or sample.get("members_area_subdomain")

    print(f"  Discovered subdomain: {subdomain!r}")
    print()

    leaf_calls = []

    # Club tools (if subdomain found)
    if subdomain:
        leaf_calls.append(("get_modules", club.hotmart_modules_list(subdomain=subdomain)))
        leaf_calls.append(("get_students", club.hotmart_students_list(subdomain=subdomain)))

    if sub_code:
        leaf_calls.append(("get_subscriber_purchases",
                           subscriptions.hotmart_subscriber_purchases_list(subscriber_code=str(sub_code))))
    if prod_id:
        leaf_calls.append(("get_product_offers",
                           products.hotmart_product_offers_list(product_id=int(prod_id) if str(prod_id).isdigit() else prod_id)))
        leaf_calls.append(("get_product_plans",
                           products.hotmart_product_plans_list(product_id=int(prod_id) if str(prod_id).isdigit() else prod_id)))
        leaf_calls.append(("get_coupons",
                           coupons.hotmart_coupons_list(product_id=int(prod_id) if str(prod_id).isdigit() else prod_id)))

    # Events: no good ID source — skip, document as untested
    # (event_id is int; passing placeholder would give misleading 400/404)

    for name, coro in leaf_calls:
        r = await safe_call(name, coro)
        results.append(r)
        flag = "✅" if r["ok"] else "❌"
        print(f"  {flag} {name:35s} {r['duration_ms']:>5}ms  {r.get('error_msg', r.get('shape',''))[:80]}")

    # ── Wave 3: club leaves (after we got module_id / user_id) ──
    r_mods = find("get_modules")
    if r_mods:
        ids["module_id"] = _extract_id(r_mods, "id", "module_id")
    r_studs = find("get_students")
    if r_studs:
        ids["user_id"] = _extract_id(r_studs, "id", "user_id", "ucode")

    print()
    print("═══ WAVE 3 — club leaves ═══")
    if subdomain and ids.get("module_id"):
        r = await safe_call("get_module_pages",
                            club.hotmart_module_pages_list(module_id=str(ids["module_id"]), subdomain=subdomain))
        results.append(r)
        flag = "✅" if r["ok"] else "❌"
        print(f"  {flag} get_module_pages                     {r['duration_ms']:>5}ms  {r.get('error_msg', r.get('shape',''))[:80]}")
    else:
        print("  ⏭️  get_module_pages skipped (no subdomain or module_id)")
    if subdomain and ids.get("user_id"):
        r = await safe_call("get_student_progress",
                            club.hotmart_student_progress_get(user_id=str(ids["user_id"]), subdomain=subdomain))
        results.append(r)
        flag = "✅" if r["ok"] else "❌"
        print(f"  {flag} get_student_progress                 {r['duration_ms']:>5}ms  {r.get('error_msg', r.get('shape',''))[:80]}")
    else:
        print("  ⏭️  get_student_progress skipped (no subdomain or user_id)")

    # ── Save ──
    out_path = Path(__file__).resolve().parent / "test-results.json"
    out_path.write_text(json.dumps({
        "discovered_ids": ids,
        "results": results,
        "summary": {
            "total": len(results),
            "ok": sum(1 for r in results if r["ok"]),
            "fail": sum(1 for r in results if not r["ok"]),
        },
    }, indent=2, ensure_ascii=False, default=str))

    print()
    summary = sum(1 for r in results if r["ok"]), len(results)
    print(f"═══ SUMMARY: {summary[0]}/{summary[1]} passed ═══")
    print(f"Full output: {out_path}")


if __name__ == "__main__":
    asyncio.run(main())
