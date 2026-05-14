"""Sales dashboards — Prefab UI apps (schema-validated via Pydantic)."""
from __future__ import annotations

from collections import Counter, defaultdict
from typing import Optional

from prefab_ui import PrefabApp
from prefab_ui.components import (
    Card, CardContent, CardHeader, CardTitle, Column, DataTable,
    DataTableColumn, Grid, Heading, Metric,
)
from prefab_ui.components.charts import BarChart, ChartSeries, LineChart, PieChart

from hotmart_mcp._shared import get_client
from hotmart_mcp.models import SaleCommission, SaleHistory
from hotmart_mcp.apps._helpers import (
    epoch_ms_to_date, format_brl, parse_items,
)


async def hotmart_sales_dashboard_app(
    start_date: Optional[int] = None,
    end_date: Optional[int] = None,
    product_id: Optional[int] = None,
) -> PrefabApp:
    """Painel visual de vendas Hotmart no período.

    Cards de métricas (receita total, ticket médio, qtd) + LineChart
    vendas/dia + PieChart por payment_type + DataTable. Use quando o
    usuário pedir 'dashboard de vendas', 'painel de vendas', 'visão
    geral das vendas do mês'.

    Args:
        start_date: Start date. Unix timestamp in milliseconds.
        end_date: End date. Unix timestamp in milliseconds.
        product_id: Optional product_id filter.
    """
    client = get_client()
    params: dict = {"max_results": 100}
    if start_date is not None: params["start_date"] = start_date
    if end_date is not None: params["end_date"] = end_date
    if product_id is not None: params["product_id"] = product_id

    raw = await client.get("/payments/api/v1/sales/history", params=params)
    items: list[SaleHistory] = parse_items(raw, SaleHistory)

    def _value(item: SaleHistory) -> float:
        p = item.purchase
        if p and p.price and p.price.value is not None:
            return p.price.value
        return 0.0

    total_qty = len(items)
    total_revenue = sum(_value(i) for i in items)
    avg_ticket = (total_revenue / total_qty) if total_qty else 0

    by_day: dict[str, float] = defaultdict(float)
    by_payment: Counter[str] = Counter()
    for it in items:
        p = it.purchase
        if not p: continue
        day = epoch_ms_to_date(p.order_date or p.approved_date)
        if day:
            by_day[day] += _value(it)
        pt = (p.payment.type.value if p.payment and p.payment.type else None) or "UNKNOWN"
        by_payment[pt] += 1

    daily_series = [{"date": d, "revenue": v} for d, v in sorted(by_day.items())]
    payment_data = [{"name": k, "value": v} for k, v in by_payment.most_common()]

    rows = []
    for it in items[:50]:
        p = it.purchase
        rows.append({
            "transaction": (p.transaction if p else None) or "?",
            "date": epoch_ms_to_date(p.order_date or p.approved_date) if p else "",
            "buyer": (it.buyer.name if it.buyer else None) or "?",
            "product": (it.product.name if it.product else None) or "?",
            "value": format_brl(_value(it)),
            "status": (p.status.value if p and p.status else None) or "?",
            "payment": (p.payment.type.value if p and p.payment and p.payment.type else None) or "?",
        })

    sanity_warning = total_qty > 0 and total_revenue == 0

    with PrefabApp() as app:
        with Column(gap=4, css_class="p-6"):
            Heading(content="Painel de Vendas Hotmart")

            if sanity_warning:
                Heading(content="⚠️ Receita zerada com vendas no período — possível schema drift", level=3)

            with Grid(columns=[1, 1, 1], gap=4):
                with Card():
                    with CardHeader():
                        CardTitle(content="Receita total")
                    with CardContent():
                        Metric(label="Receita", value=format_brl(total_revenue))
                with Card():
                    with CardHeader():
                        CardTitle(content="Vendas")
                    with CardContent():
                        Metric(label="Quantidade", value=str(total_qty))
                with Card():
                    with CardHeader():
                        CardTitle(content="Ticket médio")
                    with CardContent():
                        Metric(label="Média", value=format_brl(avg_ticket))

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
    """Breakdown de vendas — top produtos + top compradores.

    BarChart de produtos por receita + DataTable de compradores únicos.
    Use pra 'quais produtos vendem mais', 'top compradores', 'analise de
    quem está comprando'.

    Args:
        start_date: Start date. Unix timestamp in milliseconds.
        end_date: End date. Unix timestamp in milliseconds.
    """
    client = get_client()
    params: dict = {"max_results": 100}
    if start_date is not None: params["start_date"] = start_date
    if end_date is not None: params["end_date"] = end_date

    raw = await client.get("/payments/api/v1/sales/history", params=params)
    items: list[SaleHistory] = parse_items(raw, SaleHistory)

    by_product: dict[str, dict] = defaultdict(lambda: {"qty": 0, "revenue": 0.0})
    by_buyer: dict[str, dict] = defaultdict(lambda: {"qty": 0, "spent": 0.0, "name": ""})

    for it in items:
        prod = (it.product.name if it.product else None) or "?"
        buyer_email = (it.buyer.email if it.buyer else None)
        buyer_name = (it.buyer.name if it.buyer else None)
        buyer_key = buyer_email or buyer_name or "?"
        value = 0.0
        if it.purchase and it.purchase.price and it.purchase.price.value is not None:
            value = it.purchase.price.value

        by_product[prod]["qty"] += 1
        by_product[prod]["revenue"] += value
        by_buyer[buyer_key]["qty"] += 1
        by_buyer[buyer_key]["spent"] += value
        by_buyer[buyer_key]["name"] = buyer_name or buyer_key

    products_data = sorted(
        [{"product": k, "qty": v["qty"], "revenue": v["revenue"]} for k, v in by_product.items()],
        key=lambda x: x["revenue"],
        reverse=True,
    )[:15]

    buyers_rows = sorted(
        [{"name": v["name"], "email": k, "qty": v["qty"], "spent": format_brl(v["spent"])}
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
    params: dict = {"max_results": 100}
    if start_date is not None: params["start_date"] = start_date
    if end_date is not None: params["end_date"] = end_date
    if commission_as: params["commission_as"] = commission_as

    raw = await client.get("/payments/api/v1/sales/commissions", params=params)
    sales: list[SaleCommission] = parse_items(raw, SaleCommission)

    rows = []
    by_user: dict[str, float] = defaultdict(float)
    total = 0.0
    for s in sales:
        for c in (s.commissions or []):
            value = (c.commission.value if c.commission and c.commission.value is not None else 0.0)
            total += value
            user_name = (c.user.name if c.user else None) or "?"
            by_user[user_name] += value
            if len(rows) < 100:
                rows.append({
                    "user": user_name,
                    "ucode": (c.user.ucode if c.user else None) or "",
                    "role": (c.source.value if c.source else None) or "?",
                    "transaction": s.transaction or "?",
                    "product": (s.product.name if s.product else None) or "?",
                    "value": format_brl(value),
                })

    user_data = sorted(
        [{"user": k, "total": v} for k, v in by_user.items()],
        key=lambda x: x["total"],
        reverse=True,
    )[:20]

    with PrefabApp() as app:
        with Column(gap=4, css_class="p-6"):
            Heading(content="Painel de Comissões")

            with Grid(columns=[1, 1], gap=4):
                with Card():
                    with CardHeader():
                        CardTitle(content="Total no período")
                    with CardContent():
                        Metric(label="Comissões", value=format_brl(total))
                with Card():
                    with CardHeader():
                        CardTitle(content="Itens")
                    with CardContent():
                        Metric(label="Quantidade", value=str(len(sales)))

            with Card():
                with CardHeader():
                    CardTitle(content="Top 20 por afiliado")
                with CardContent():
                    BarChart(
                        data=user_data,
                        series=[ChartSeries(data_key="total", label="Comissão R$")],
                        x_axis="user",
                    )

            with Card():
                with CardHeader():
                    CardTitle(content=f"Detalhe ({len(rows)} itens)")
                with CardContent():
                    DataTable(
                        columns=[
                            DataTableColumn(key="user", header="Afiliado", sortable=True),
                            DataTableColumn(key="ucode", header="UCode"),
                            DataTableColumn(key="role", header="Papel", sortable=True),
                            DataTableColumn(key="transaction", header="Transação", sortable=True),
                            DataTableColumn(key="product", header="Produto", sortable=True),
                            DataTableColumn(key="value", header="Comissão"),
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
