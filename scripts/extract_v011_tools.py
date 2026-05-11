#!/usr/bin/env python3
"""Extract tool descriptions from v0.1.1 (commit 799ee01) for A/B comparison."""
import ast
import json
import subprocess
from pathlib import Path

OUT = Path(__file__).resolve().parent / "eval-cases-v011.json"
TOOLS = ["club", "coupons", "negotiation", "products", "sales", "subscriptions", "tickets"]

tools_out = []
for t in TOOLS:
    src = subprocess.check_output(
        ["git", "show", f"799ee01:src/hotmart_mcp/tools/{t}.py"], text=True
    )
    tree = ast.parse(src)
    for node in tree.body:
        if isinstance(node, ast.AsyncFunctionDef):
            doc = ast.get_docstring(node) or ""
            head = doc.split("\n    Args:")[0].split("\nArgs:")[0].strip()
            tools_out.append({
                "name": node.name,
                "description": head,
                "module": t,
            })

# Load v0.2.0 cases and remap expected_tool back to v0.1.1 names
v020 = json.loads((Path(__file__).resolve().parent / "eval-cases.json").read_text())
name_map_020_to_011 = {
    "hotmart_sales_history_list": "get_sales_history",
    "hotmart_sales_summary_list": "get_sales_summary",
    "hotmart_sales_participants_list": "get_sales_participants",
    "hotmart_sales_commissions_list": "get_sales_commissions",
    "hotmart_sales_price_details_list": "get_sales_price_details",
    "hotmart_sale_refund": "refund_sale",
    "hotmart_subscriptions_list": "get_subscriptions",
    "hotmart_subscriptions_summary_list": "get_subscriptions_summary",
    "hotmart_subscription_transactions_list": "get_subscription_transactions",
    "hotmart_subscriber_purchases_list": "get_subscriber_purchases",
    "hotmart_subscription_cancel": "cancel_subscription",
    "hotmart_batch_subscriptions_cancel": "batch_cancel_subscriptions",
    "hotmart_subscription_reactivate": "reactivate_subscription",
    "hotmart_batch_subscriptions_reactivate": "batch_reactivate_subscriptions",
    "hotmart_subscription_due_day_update": "change_subscription_due_day",
    "hotmart_modules_list": "get_modules",
    "hotmart_module_pages_list": "get_module_pages",
    "hotmart_students_list": "get_students",
    "hotmart_student_progress_get": "get_student_progress",
    "hotmart_products_list": "list_products",
    "hotmart_product_offers_list": "get_product_offers",
    "hotmart_product_plans_list": "get_product_plans",
    "hotmart_coupon_create": "create_coupon",
    "hotmart_coupons_list": "get_coupons",
    "hotmart_coupon_delete": "delete_coupon",
    "hotmart_event_info_get": "get_event_info",
    "hotmart_event_participants_list": "get_event_participants",
    "hotmart_negotiation_generate": "generate_negotiation",
}
cases = []
for c in v020["cases"]:
    cases.append({
        "id": c["id"],
        "prompt_pt": c["prompt_pt"],
        "expected_tool": name_map_020_to_011.get(c["expected_tool"], c["expected_tool"]),
        "ambiguous_alt": name_map_020_to_011.get(c["ambiguous_alt"]) if c["ambiguous_alt"] else None,
    })

OUT.write_text(json.dumps({"tools": tools_out, "cases": cases}, indent=2, ensure_ascii=False))
tool_names_011 = {t["name"] for t in tools_out}
missing = [c["expected_tool"] for c in cases if c["expected_tool"] not in tool_names_011]
print(f"✅ v0.1.1 eval cases: {OUT}")
print(f"   tools: {len(tools_out)}")
print(f"   cases: {len(cases)}")
if missing:
    print(f"   ⚠️ missing in v0.1.1: {missing}")
