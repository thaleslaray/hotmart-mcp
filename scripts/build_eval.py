#!/usr/bin/env python3
"""Extract tool descriptions + build PT-BR eval prompts for the 28 Hotmart tools.

Output: scripts/eval-cases.json
    {
      "tools": [{"name": str, "description": str, "params": [str]}],
      "cases": [{"prompt_pt": str, "expected_tool": str, "ambiguous_alt": str|None}]
    }
"""
from __future__ import annotations

import ast
import json
import re
from pathlib import Path


TOOLS_DIR = Path(__file__).resolve().parent.parent / "src" / "hotmart_mcp" / "tools"
OUT = Path(__file__).resolve().parent / "eval-cases.json"


def extract_tools() -> list[dict]:
    """Extract tool name + tool-level description + per-param description.

    FastMCP exposes BOTH to the LLM client:
    - tool description = head (before Args:)
    - inputSchema.properties[name].description = each Args: line

    The eval judge must see BOTH to be fair.
    """
    tools: list[dict] = []
    for py in sorted(TOOLS_DIR.glob("*.py")):
        if py.name.startswith("_"):
            continue
        tree = ast.parse(py.read_text())
        for node in tree.body:
            if isinstance(node, ast.AsyncFunctionDef) and node.name.startswith("hotmart_"):
                doc = ast.get_docstring(node) or ""
                if "\n    Args:" in doc:
                    head, args_block = doc.split("\n    Args:", 1)
                elif "\nArgs:" in doc:
                    head, args_block = doc.split("\nArgs:", 1)
                else:
                    head, args_block = doc, ""
                head = head.strip()

                # parse Args: into {param_name: desc}
                param_descs: dict[str, str] = {}
                if args_block:
                    current_param: str | None = None
                    buf: list[str] = []
                    for raw in args_block.splitlines():
                        line = raw.rstrip()
                        m = re.match(r"^    ([a-zA-Z_][a-zA-Z0-9_]*):\s*(.*)$", line)
                        if m:
                            if current_param:
                                param_descs[current_param] = "\n".join(buf).strip()
                            current_param = m.group(1)
                            buf = [m.group(2)]
                        elif current_param and line.strip():
                            buf.append(line.strip())
                    if current_param:
                        param_descs[current_param] = "\n".join(buf).strip()

                params_full = [
                    {"name": a.arg, "description": param_descs.get(a.arg, "")}
                    for a in node.args.args
                    if a.arg not in ("self",)
                ]
                tools.append({
                    "name": node.name,
                    "description": head,
                    "params": params_full,
                    "module": py.stem,
                })
    return tools


# 28 realistic PT-BR prompts, ordered to match the tool roster.
# A prompt should *uniquely* steer to one tool, except for `ambiguous_alt`
# which lists confusable alternates (used to test disambiguation).
PROMPTS = [
    # sales
    ("me mostra as vendas do último mês pra eu ver transação por transação",
        "hotmart_sales_history_list", "hotmart_sales_summary_list"),
    ("quanto faturei esse ano? quero o total agregado, não o detalhe",
        "hotmart_sales_summary_list", "hotmart_sales_history_list"),
    ("lista os compradores das minhas vendas recentes",
        "hotmart_sales_participants_list", None),
    ("quero ver as comissões que recebi como afiliado",
        "hotmart_sales_commissions_list", None),
    ("detalhe de preço (impostos, taxas) das últimas vendas",
        "hotmart_sales_price_details_list", None),
    ("preciso estornar a venda com código HP2890253164",
        "hotmart_sale_refund", None),
    # subscriptions
    ("me lista todas as assinaturas ativas dos meus produtos",
        "hotmart_subscriptions_list", "hotmart_subscriptions_summary_list"),
    ("quantas assinaturas ativas eu tenho no total por status?",
        "hotmart_subscriptions_summary_list", "hotmart_subscriptions_list"),
    ("histórico de cobranças/pagamentos de assinatura — quero ver as transações",
        "hotmart_subscription_transactions_list", "hotmart_subscriptions_list"),
    ("as compras de um assinante específico — código VRWIQQRG",
        "hotmart_subscriber_purchases_list", None),
    ("cancela a assinatura VRWIQQRG agora",
        "hotmart_subscription_cancel", "hotmart_batch_subscriptions_cancel"),
    ("cancela essas 50 assinaturas em lote: ABC, DEF, GHI...",
        "hotmart_batch_subscriptions_cancel", "hotmart_subscription_cancel"),
    ("reativa a assinatura VRWIQQRG",
        "hotmart_subscription_reactivate", "hotmart_batch_subscriptions_reactivate"),
    ("reativa essas 30 assinaturas todas de uma vez",
        "hotmart_batch_subscriptions_reactivate", "hotmart_subscription_reactivate"),
    ("muda o dia de vencimento da assinatura VRWIQQRG pra dia 10",
        "hotmart_subscription_due_day_update", None),
    # club
    ("quais módulos eu tenho na minha área de membros? subdomínio é afantasticafabricadasautomacoe",
        "hotmart_modules_list", "hotmart_module_pages_list"),
    ("dentro do módulo 12345, me lista todas as páginas/aulas",
        "hotmart_module_pages_list", "hotmart_modules_list"),
    ("quais alunos tenho cadastrados na área de membros?",
        "hotmart_students_list", None),
    ("o aluno V7yQbq3z7J completou quais aulas?",
        "hotmart_student_progress_get", None),
    # products
    ("me lista todos os produtos cadastrados na minha conta Hotmart",
        "hotmart_products_list", None),
    ("quais ofertas (preços/condições) tem o produto 4168346?",
        "hotmart_product_offers_list", "hotmart_product_plans_list"),
    ("quais planos de assinatura existem pro produto 4168346?",
        "hotmart_product_plans_list", "hotmart_product_offers_list"),
    # coupons
    ("cria um cupom de 10% pro produto 4168346 com código BLACKFRIDAY",
        "hotmart_coupon_create", None),
    ("lista os cupons ativos do produto 4168346",
        "hotmart_coupons_list", None),
    ("apaga o cupom de id 99999",
        "hotmart_coupon_delete", None),
    # tickets
    ("informações do evento 5655136 — datas, lotes, etc",
        "hotmart_event_info_get", "hotmart_event_participants_list"),
    ("quem comprou ingresso pro evento 5655136?",
        "hotmart_event_participants_list", "hotmart_event_info_get"),
    # negotiation
    ("o aluno tá inadimplente — gera uma negociação parcelada pra ele",
        "hotmart_negotiation_generate", None),
]


def main():
    tools = extract_tools()
    cases = [
        {"id": i + 1, "prompt_pt": p, "expected_tool": exp, "ambiguous_alt": alt}
        for i, (p, exp, alt) in enumerate(PROMPTS)
    ]
    # sanity: every expected tool exists
    tool_names = {t["name"] for t in tools}
    missing = [c["expected_tool"] for c in cases if c["expected_tool"] not in tool_names]
    if missing:
        print(f"⚠️ expected tools not found in generated code: {missing}")

    OUT.write_text(json.dumps({"tools": tools, "cases": cases}, indent=2, ensure_ascii=False))
    print(f"✅ Eval cases written to {OUT}")
    print(f"   tools: {len(tools)}")
    print(f"   cases: {len(cases)}")
    ambig = sum(1 for c in cases if c["ambiguous_alt"])
    print(f"   cases with ambiguous alternative: {ambig}")


if __name__ == "__main__":
    main()
