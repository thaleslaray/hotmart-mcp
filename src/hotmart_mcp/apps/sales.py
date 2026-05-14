"""Sales dashboards — Prefab UI apps."""
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


async def hotmart_sales_dashboard_app(
    start_date: Optional[int] = None,
    end_date: Optional[int] = None,
    product_id: Optional[int] = None,
) -> PrefabApp:
    """Painel visual de vendas Hotmart no período.

    Renderiza cards de métricas (receita total, ticket médio, qtd vendas)
    + LineChart de vendas por dia + PieChart por payment_type + DataTable.
    Use quando o usuário pedir 'dashboard de vendas', 'painel de vendas',
    'visão geral das vendas do mês'.

    Args:
        start_date: Start date. Unix timestamp in milliseconds.
        end_date: End date. Unix timestamp in milliseconds.
        product_id: Optional product_id filter.
    """
    client = get_client()
    params = {"max_results": 100}
    if start_date is not None: params["start_date"] = start_date
    if end_date is not None: params["end_date"] = end_date
    if product_id is not None: params["product_id"] = product_id

    history = await client.get("/payments/api/v1/sales/history", params=params)
    items = history.get("items", []) if isinstance(history, dict) else []

    total_qty = len(items)
    total_revenue = sum((i.get("price", {}) or {}).get("value", 0) or 0 for i in items)
    avg_ticket = (total_revenue / total_qty) if total_qty else 0

    by_day: dict[str, float] = defaultdict(float)
    by_payment: Counter[str] = Counter()
    for it in items:
        purchase = it.get("purchase", {}) or {}
        day = _epoch_ms_to_date(purchase.get("order_date") or purchase.get("approved_date"))
        if day:
            by_day[day] += (it.get("price", {}) or {}).get("value", 0) or 0
        pt = (purchase.get("payment", {}) or {}).get("type") or "UNKNOWN"
        by_payment[pt] += 1

    daily_series = [{"date": d, "revenue": v} for d, v in sorted(by_day.items())]
    payment_data = [{"name": k, "value": v} for k, v in by_payment.most_common()]

    rows = []
    for it in items[:50]:
        purchase = it.get("purchase", {}) or {}
        buyer = it.get("buyer", {}) or {}
        rows.append({
            "transaction": purchase.get("transaction") or "?",
            "date": _epoch_ms_to_date(purchase.get("order_date") or purchase.get("approved_date")),
            "buyer": buyer.get("name") or "?",
            "product": (it.get("product", {}) or {}).get("name") or "?",
            "value": _format_brl((it.get("price", {}) or {}).get("value", 0) or 0),
            "status": purchase.get("transaction_status") or "?",
            "payment": (purchase.get("payment", {}) or {}).get("type") or "?",
        })

    with PrefabApp() as app:
        with Column(gap=4, css_class="p-6"):
            Heading(content="Painel de Vendas Hotmart")

            with Grid(columns=[1, 1, 1], gap=4):
                with Card():
                    with CardHeader():
                        CardTitle(content="Receita total")
                    with CardContent():
                        Metric(label="Receita", value=_format_brl(total_revenue))
                with Card():
                    with CardHeader():
                        CardTitle(content="Vendas")
                    with CardContent():
                        Metric(label="Quantidade", value=str(total_qty))
                with Card():
                    with CardHeader():
                        CardTitle(content="Ticket médio")
                    with CardContent():
                        Metric(label="Média", value=_format_brl(avg_ticket))

            with Grid(columns=[2, 1], gap=4):
                with Card():
                    with CardHeader():
                        CardTitle(content="Receita por dia")
                    with CardContent():
                        LineChart(
                            data=daily_series,
                            series=[ChartSeries(data_key="revenue", label="Receita")],
                            x_axis="date",
                        )
                with Card():
                    with CardHeader():
                        CardTitle(content="Por forma de pagamento")
                    with CardContent():
                        PieChart(
                            data=payment_data,
                            data_key="value",
                            name_key="name",
                        )

            with Card():
                with CardHeader():
                    CardTitle(content=f"Últimas transações (top 50 de {total_qty})")
                with CardContent():
                    DataTable(
                        columns=[
                            DataTableColumn(key="transaction", header="Transação"),
                            DataTableColumn(key="date", header="Data", sortable=True),
                            DataTableColumn(key="buyer", header="Comprador", sortable=True),
                            DataTableColumn(key="product", header="Produto", sortable=True),
                            DataTableColumn(key="value", header="Valor"),
                            DataTableColumn(key="status", header="Status", sortable=True),
                            DataTableColumn(key="payment", header="Pagamento"),
                        ],
                        rows=rows,
                        search=True,
                    )

    return app


async def hotmart_sales_breakdown_app(
    start_date: Optional[int] = None,
    end_date: Optional[int] = None,
) -> PrefabApp:
    """Vendas detalhadas por produto + top compradores.

    BarChart com vendas por produto + DataTable rankeada dos top buyers.
    Use quando o usuário pedir 'breakdown de vendas', 'top produtos',
    'meus melhores compradores'.

    Args:
        start_date: Start date. Unix timestamp in milliseconds.
        end_date: End date. Unix timestamp in milliseconds.
    """
    client = get_client()
    params = {"max_results": 100}
    if start_date is not None: params["start_date"] = start_date
    if end_date is not None: params["end_date"] = end_date

    history = await client.get("/payments/api/v1/sales/history", params=params)
    items = history.get("items", []) if isinstance(history, dict) else []

    by_product: dict[str, dict] = defaultdict(lambda: {"qty": 0, "revenue": 0.0})
    by_buyer: dict[str, dict] = defaultdict(lambda: {"qty": 0, "spent": 0.0, "name": ""})

    for it in items:
        prod = (it.get("product", {}) or {}).get("name") or "?"
        buyer = it.get("buyer", {}) or {}
        buyer_key = buyer.get("email") or buyer.get("name") or "?"
        value = (it.get("price", {}) or {}).get("value", 0) or 0

        by_product[prod]["qty"] += 1
        by_product[prod]["revenue"] += value
        by_buyer[buyer_key]["qty"] += 1
        by_buyer[buyer_key]["spent"] += value
        by_buyer[buyer_key]["name"] = buyer.get("name") or buyer_key

    products_data = sorted(
        [{"product": k, "qty": v["qty"], "revenue": v["revenue"]} for k, v in by_product.items()],
        key=lambda x: x["revenue"],
        reverse=True,
    )[:15]

    buyers_rows = sorted(
        [{"name": v["name"], "email": k, "qty": v["qty"], "spent": _format_brl(v["spent"])}
         for k, v in by_buyer.items()],
        key=lambda x: x["qty"],
        reverse=True,
    )[:50]

    with PrefabApp() as app:
        with Column(gap=4, css_class="p-6"):
            Heading(content="Breakdown de Vendas")

            with Card():
                with CardHeader():
                    CardTitle(content="Vendas por produto (top 15)")
                with CardContent():
                    BarChart(
                        data=products_data,
                        series=[
                            ChartSeries(data_key="qty", label="Qty"),
                            ChartSeries(data_key="revenue", label="Receita R$"),
                        ],
                        x_axis="product",
                    )

            with Card():
                with CardHeader():
                    CardTitle(content=f"Top compradores ({len(by_buyer)} únicos)")
                with CardContent():
                    DataTable(
                        columns=[
                            DataTableColumn(key="name", header="Comprador", sortable=True),
                            DataTableColumn(key="email", header="Email"),
                            DataTableColumn(key="qty", header="Compras", sortable=True),
                            DataTableColumn(key="spent", header="Total gasto"),
                        ],
                        rows=buyers_rows,
                        search=True,
                    )

    return app


async def hotmart_commissions_dashboard_app(
    start_date: Optional[int] = None,
    end_date: Optional[int] = None,
    commission_as: Optional[str] = None,
) -> PrefabApp:
    """Painel de comissões — total a pagar/receber por afiliado.

    DataTable com afiliado/papel/valor + Metric de total. Use pra
    'comissões do mês', 'quanto pagar pros afiliados', 'settlement'.

    Args:
        start_date: Start date. Unix timestamp in milliseconds.
        end_date: End date. Unix timestamp in milliseconds.
        commission_as: PRODUCER | COPRODUCER | AFFILIATE.
    """
    client = get_client()
    params = {"max_results": 100}
    if start_date is not None: params["start_date"] = start_date
    if end_date is not None: params["end_date"] = end_date
    if commission_as: params["commission_as"] = commission_as

    res = await client.get("/payments/api/v1/sales/commissions", params=params)
    items = res.get("items", []) if isinstance(res, dict) else []

    total = sum((i.get("commission_value", 0) or 0) for i in items)
    by_user: dict[str, float] = defaultdict(float)

    rows = []
    for it in items[:100]:
        user = it.get("user", {}) or {}
        commission_value = it.get("commission_value", 0) or 0
        by_user[user.get("name") or user.get("email") or "?"] += commission_value
        rows.append({
            "user": user.get("name") or "?",
            "email": user.get("email") or "",
            "role": it.get("commission_as") or "?",
            "transaction": (it.get("purchase", {}) or {}).get("transaction") or "?",
            "product": (it.get("product", {}) or {}).get("name") or "?",
            "value": _format_brl(commission_value),
        })

    by_user_data = [{"user": k, "value": v} for k, v in sorted(by_user.items(), key=lambda x: x[1], reverse=True)[:10]]

    with PrefabApp() as app:
        with Column(gap=4, css_class="p-6"):
            Heading(content="Comissões")

            with Grid(columns=[1, 1], gap=4):
                with Card():
                    with CardHeader():
                        CardTitle(content="Total no período")
                    with CardContent():
                        Metric(label="Comissões", value=_format_brl(total))
                with Card():
                    with CardHeader():
                        CardTitle(content="Top afiliados")
                    with CardContent():
                        BarChart(
                            data=by_user_data,
                            series=[ChartSeries(data_key="value", label="Comissão R$")],
                            x_axis="user",
                        )

            with Card():
                with CardHeader():
                    CardTitle(content=f"Detalhes ({len(items)} comissões)")
                with CardContent():
                    DataTable(
                        columns=[
                            DataTableColumn(key="user", header="Afiliado", sortable=True),
                            DataTableColumn(key="email", header="Email"),
                            DataTableColumn(key="role", header="Papel", sortable=True),
                            DataTableColumn(key="product", header="Produto", sortable=True),
                            DataTableColumn(key="transaction", header="Transação"),
                            DataTableColumn(key="value", header="Valor"),
                        ],
                        rows=rows,
                        search=True,
                    )

    return app


__all__ = [
    "hotmart_sales_dashboard_app",
    "hotmart_sales_breakdown_app",
    "hotmart_commissions_dashboard_app",
]
