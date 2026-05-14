"""Subscriptions dashboards — Prefab UI apps (schema-validated)."""
from __future__ import annotations

from collections import Counter, defaultdict
from typing import Optional

from prefab_ui import PrefabApp
from prefab_ui.components import (
    Card, CardContent, CardHeader, CardTitle, Column, DataTable,
    DataTableColumn, Grid, Heading, Metric,
)
from prefab_ui.components.charts import ChartSeries, LineChart, PieChart

from hotmart_mcp._shared import get_client
from hotmart_mcp.models import Subscription, SubscriberPurchase
from hotmart_mcp.apps._helpers import (
    epoch_ms_to_date, format_brl, parse_items,
)


async def hotmart_subscriptions_health_app(
    product_id: Optional[int] = None,
) -> PrefabApp:
    """Painel de saúde das assinaturas — counts por status + lista.

    Grid com cards (ativos, atrasados, cancelados) + PieChart breakdown
    + DataTable. Use pra 'saúde das assinaturas', 'visão geral das
    assinaturas', 'quantos assinantes ativos'.

    Args:
        product_id: Optional product_id filter.
    """
    client = get_client()
    params: dict = {"max_results": 100}
    if product_id: params["product_id"] = product_id

    raw = await client.get("/payments/api/v1/subscriptions", params=params)
    items: list[Subscription] = parse_items(raw, Subscription)

    by_status: Counter[str] = Counter()
    for it in items:
        by_status[it.status.value if it.status else "?"] += 1

    pie_data = [{"name": k, "value": v} for k, v in by_status.most_common()]

    rows = []
    for it in items[:100]:
        rows.append({
            "code": it.subscriber_code or "?",
            "subscriber": (it.subscriber.name if it.subscriber else None) or "?",
            "email": (it.subscriber.email if it.subscriber else None) or "",
            "product": (it.product.name if it.product else None) or "?",
            "plan": (it.plan.name if it.plan else None) or "?",
            "status": (it.status.value if it.status else None) or "?",
            "accession": epoch_ms_to_date(it.accession_date),
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
                        CardTitle(content=f"Assinaturas ({len(items)} no período)")
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
    """Análise de churn — cancelamentos por período + tendência.

    LineChart cancelamentos no tempo + DataTable de recentes. Use pra
    'análise de churn', 'cancelamentos da semana', 'taxa de cancelamento'.

    Args:
        product_id: Optional product_id filter.
    """
    client = get_client()
    params: dict = {"max_results": 200}
    if product_id: params["product_id"] = product_id

    raw = await client.get("/payments/api/v1/subscriptions", params=params)
    items: list[Subscription] = parse_items(raw, Subscription)

    def _status_str(s: Subscription) -> str:
        return s.status.value if s.status else ""

    cancelled = [i for i in items if _status_str(i).startswith("CANCELLED")]
    active = [i for i in items if _status_str(i) == "ACTIVE"]
    rate = (len(cancelled) / len(items) * 100) if items else 0

    by_day: dict[str, int] = defaultdict(int)
    for c in cancelled:
        d = epoch_ms_to_date(c.date_next_charge or c.accession_date)
        if d:
            by_day[d] += 1

    daily = [{"date": d, "count": v} for d, v in sorted(by_day.items())]

    rows = []
    for c in cancelled[:100]:
        rows.append({
            "code": c.subscriber_code or "?",
            "subscriber": (c.subscriber.name if c.subscriber else None) or "?",
            "product": (c.product.name if c.product else None) or "?",
            "status": _status_str(c) or "?",
            "since": epoch_ms_to_date(c.accession_date),
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
    """Visão 360 de um assinante — perfil + histórico de compras.

    Cards de LTV/qty/ticket + DataTable com purchases. Use pra 'ver
    dados do assinante X', 'histórico completo do código Y'.

    Args:
        subscriber_code: Subscriber code (Hotmart alphanumeric, ex: 'VRWIQQRG').
    """
    client = get_client()
    raw = await client.get(
        f"/payments/api/v1/subscriptions/{subscriber_code}/purchases"
    )
    purchases: list[SubscriberPurchase] = parse_items(raw, SubscriberPurchase)

    def _value(p: SubscriberPurchase) -> float:
        if p.price and p.price.value is not None:
            return p.price.value
        return 0.0

    total_spent = sum(_value(p) for p in purchases)
    qty = len(purchases)
    sanity_warning = qty > 0 and total_spent == 0

    rows = []
    for p in purchases[:100]:
        rows.append({
            "transaction": p.transaction or "?",
            "date": epoch_ms_to_date(p.approved_date),
            "recurrence": str(p.recurrency_number) if p.recurrency_number else "—",
            "value": format_brl(_value(p)),
            "status": (p.status.value if p.status else None) or "?",
            "payment": (p.payment_type.value if p.payment_type else None) or "—",
        })

    with PrefabApp() as app:
        with Column(gap=4, css_class="p-6"):
            Heading(content=f"Assinante {subscriber_code}")

            if sanity_warning:
                Heading(content="⚠️ LTV zerado com compras no histórico — possível schema drift", level=3)

            with Grid(columns=[1, 1, 1], gap=4):
                with Card():
                    with CardHeader():
                        CardTitle(content="Total gasto (LTV)")
                    with CardContent():
                        Metric(label="LTV", value=format_brl(total_spent))
                with Card():
                    with CardHeader():
                        CardTitle(content="Total de compras")
                    with CardContent():
                        Metric(label="Compras", value=str(qty))
                with Card():
                    with CardHeader():
                        CardTitle(content="Ticket médio")
                    with CardContent():
                        Metric(
                            label="Médio",
                            value=format_brl(total_spent / qty) if qty else "—",
                        )

            with Card():
                with CardHeader():
                    CardTitle(content="Histórico de compras")
                with CardContent():
                    DataTable(
                        columns=[
                            DataTableColumn(key="transaction", header="Transação"),
                            DataTableColumn(key="date", header="Data", sortable=True),
                            DataTableColumn(key="recurrence", header="Recorrência"),
                            DataTableColumn(key="value", header="Valor"),
                            DataTableColumn(key="status", header="Status", sortable=True),
                            DataTableColumn(key="payment", header="Pagamento"),
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
