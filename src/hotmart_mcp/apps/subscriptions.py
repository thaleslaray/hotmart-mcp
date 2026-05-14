"""Subscriptions dashboards — Prefab UI apps."""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime
from typing import Optional

from prefab_ui import PrefabApp
from prefab_ui.components import (
    Card, CardContent, CardHeader, CardTitle, Column, DataTable,
    DataTableColumn, Grid, Heading, Metric,
)
from prefab_ui.components.charts import BarChart, ChartSeries, LineChart, PieChart

from hotmart_mcp._shared import get_client


def _format_brl(value: float | int) -> str:
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _epoch_ms_to_date(ms: int | None) -> str:
    if not ms:
        return ""
    return datetime.fromtimestamp(ms / 1000).strftime("%Y-%m-%d")


async def hotmart_subscriptions_health_app(
    product_id: Optional[int] = None,
) -> PrefabApp:
    """Painel de saúde das assinaturas — counts por status + lista filtrar.

    Grid com cards de status (ativos, cancelados, atrasados) + PieChart
    breakdown + DataTable. Use pra 'saúde das assinaturas', 'visão geral
    das assinaturas', 'quantos assinantes ativos'.

    Args:
        product_id: Optional product_id filter.
    """
    client = get_client()
    params = {"max_results": 100}
    if product_id: params["product_id"] = product_id

    summary = await client.get("/payments/api/v1/subscriptions/summary", params=params)
    items_sum = summary.get("items", []) if isinstance(summary, dict) else []

    list_res = await client.get("/payments/api/v1/subscriptions", params=params)
    items_list = list_res.get("items", []) if isinstance(list_res, dict) else []

    by_status: Counter[str] = Counter()
    for it in items_list:
        s = it.get("status") or "?"
        by_status[s] += 1

    pie_data = [{"name": k, "value": v} for k, v in by_status.most_common()]

    rows = []
    for it in items_list[:100]:
        subscriber = it.get("subscriber", {}) or {}
        product = it.get("product", {}) or {}
        plan = it.get("plan", {}) or {}
        rows.append({
            "code": subscriber.get("code") or "?",
            "subscriber": subscriber.get("name") or "?",
            "email": subscriber.get("email") or "",
            "product": product.get("name") or "?",
            "plan": plan.get("name") or "?",
            "status": it.get("status") or "?",
            "accession": _epoch_ms_to_date(it.get("accession_date")),
        })

    with PrefabApp() as app:
        with Column(gap=4, css_class="p-6"):
            Heading(content="Saúde das Assinaturas")

            with Grid(columns=[1, 1, 1, 1], gap=4):
                for status in ("ACTIVE", "DELAYED", "CANCELLED_BY_CUSTOMER", "CANCELLED_BY_SELLER"):
                    with Card():
                        with CardHeader():
                            CardTitle(content=status.replace("_", " ").title())
                        with CardContent():
                            Metric(label=status, value=str(by_status.get(status, 0)))

            with Grid(columns=[1, 2], gap=4):
                with Card():
                    with CardHeader():
                        CardTitle(content="Status breakdown")
                    with CardContent():
                        PieChart(data=pie_data, data_key="value", name_key="name")
                with Card():
                    with CardHeader():
                        CardTitle(content=f"Assinaturas ({len(items_list)} no período)")
                    with CardContent():
                        DataTable(
                            columns=[
                                DataTableColumn(key="code", header="Código"),
                                DataTableColumn(key="subscriber", header="Assinante", sortable=True),
                                DataTableColumn(key="email", header="Email"),
                                DataTableColumn(key="product", header="Produto", sortable=True),
                                DataTableColumn(key="plan", header="Plano"),
                                DataTableColumn(key="status", header="Status", sortable=True),
                                DataTableColumn(key="accession", header="Adesão", sortable=True),
                            ],
                            rows=rows,
                            search=True,
                        )
    return app


async def hotmart_churn_analyzer_app(
    product_id: Optional[int] = None,
) -> PrefabApp:
    """Análise de churn — cancelamentos por período + razões + tendência.

    LineChart cancelamentos no tempo + DataTable de cancelamentos recentes.
    Use pra 'análise de churn', 'cancelamentos da semana', 'taxa de cancelamento'.

    Args:
        product_id: Optional product_id filter.
    """
    client = get_client()
    params = {"max_results": 200}
    if product_id: params["product_id"] = product_id

    list_res = await client.get("/payments/api/v1/subscriptions", params=params)
    items = list_res.get("items", []) if isinstance(list_res, dict) else []

    cancelled = [
        i for i in items
        if (i.get("status") or "").startswith("CANCELLED")
    ]
    active = [i for i in items if i.get("status") == "ACTIVE"]

    rate = (len(cancelled) / len(items) * 100) if items else 0

    by_day: dict[str, int] = defaultdict(int)
    for c in cancelled:
        d = _epoch_ms_to_date(c.get("date_next_charge") or c.get("accession_date"))
        if d:
            by_day[d] += 1

    daily = [{"date": d, "count": v} for d, v in sorted(by_day.items())]

    rows = []
    for c in cancelled[:100]:
        subscriber = c.get("subscriber", {}) or {}
        product = c.get("product", {}) or {}
        rows.append({
            "code": subscriber.get("code") or "?",
            "subscriber": subscriber.get("name") or "?",
            "product": product.get("name") or "?",
            "status": c.get("status") or "?",
            "since": _epoch_ms_to_date(c.get("accession_date")),
        })

    with PrefabApp() as app:
        with Column(gap=4, css_class="p-6"):
            Heading(content="Análise de Churn")

            with Grid(columns=[1, 1, 1], gap=4):
                with Card():
                    with CardHeader():
                        CardTitle(content="Total cancelados")
                    with CardContent():
                        Metric(label="Cancelados", value=str(len(cancelled)))
                with Card():
                    with CardHeader():
                        CardTitle(content="Ativos")
                    with CardContent():
                        Metric(label="Ativos", value=str(len(active)))
                with Card():
                    with CardHeader():
                        CardTitle(content="Taxa de cancelamento")
                    with CardContent():
                        Metric(label="Churn rate", value=f"{rate:.1f}%")

            with Card():
                with CardHeader():
                    CardTitle(content="Cancelamentos no tempo")
                with CardContent():
                    LineChart(
                        data=daily,
                        series=[ChartSeries(data_key="count", label="Cancelamentos")],
                        x_axis="date",
                    )

            with Card():
                with CardHeader():
                    CardTitle(content=f"Cancelamentos recentes ({len(cancelled)})")
                with CardContent():
                    DataTable(
                        columns=[
                            DataTableColumn(key="code", header="Código"),
                            DataTableColumn(key="subscriber", header="Assinante", sortable=True),
                            DataTableColumn(key="product", header="Produto", sortable=True),
                            DataTableColumn(key="status", header="Status", sortable=True),
                            DataTableColumn(key="since", header="Adesão"),
                        ],
                        rows=rows,
                        search=True,
                    )
    return app


async def hotmart_subscriber_360_app(subscriber_code: str) -> PrefabApp:
    """Visão 360 de um assinante específico — perfil + histórico de compras.

    Card com perfil + DataTable com purchases. Use pra 'ver dados do
    assinante X', 'histórico completo do código Y'.

    Args:
        subscriber_code: Subscriber code (Hotmart alphanumeric, ex: 'VRWIQQRG').
    """
    client = get_client()
    res = await client.get(
        f"/payments/api/v1/subscriptions/{subscriber_code}/purchases"
    )
    items = res if isinstance(res, list) else (res.get("items", []) if isinstance(res, dict) else [])

    total_spent = sum(
        (p.get("price", {}) or {}).get("value", 0) or 0
        for p in items
    )

    rows = []
    for p in items[:100]:
        product = p.get("product", {}) or {}
        rows.append({
            "transaction": p.get("transaction") or "?",
            "date": _epoch_ms_to_date(p.get("approved_date")),
            "product": product.get("name") or "?",
            "value": _format_brl((p.get("price", {}) or {}).get("value", 0) or 0),
            "status": p.get("status") or "?",
        })

    with PrefabApp() as app:
        with Column(gap=4, css_class="p-6"):
            Heading(content=f"Assinante {subscriber_code}")

            with Grid(columns=[1, 1, 1], gap=4):
                with Card():
                    with CardHeader():
                        CardTitle(content="Total gasto")
                    with CardContent():
                        Metric(label="LTV", value=_format_brl(total_spent))
                with Card():
                    with CardHeader():
                        CardTitle(content="Total de compras")
                    with CardContent():
                        Metric(label="Compras", value=str(len(items)))
                with Card():
                    with CardHeader():
                        CardTitle(content="Ticket médio")
                    with CardContent():
                        Metric(
                            label="Médio",
                            value=_format_brl(total_spent / len(items)) if items else "—",
                        )

            with Card():
                with CardHeader():
                    CardTitle(content="Histórico de compras")
                with CardContent():
                    DataTable(
                        columns=[
                            DataTableColumn(key="transaction", header="Transação"),
                            DataTableColumn(key="date", header="Data", sortable=True),
                            DataTableColumn(key="product", header="Produto", sortable=True),
                            DataTableColumn(key="value", header="Valor"),
                            DataTableColumn(key="status", header="Status", sortable=True),
                        ],
                        rows=rows,
                        search=True,
                    )
    return app


__all__ = [
    "hotmart_subscriptions_health_app",
    "hotmart_churn_analyzer_app",
    "hotmart_subscriber_360_app",
]
