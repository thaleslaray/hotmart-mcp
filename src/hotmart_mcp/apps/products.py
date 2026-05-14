"""Products + Coupons dashboards — Prefab UI apps."""
from __future__ import annotations

from collections import Counter
from datetime import datetime
from typing import Optional

from prefab_ui import PrefabApp
from prefab_ui.components import (
    Card, CardContent, CardHeader, CardTitle, Column, DataTable,
    DataTableColumn, Grid, Heading, Metric,
)
from prefab_ui.components.charts import BarChart, ChartSeries, PieChart

from hotmart_mcp._shared import get_client


def _epoch_ms_to_date(ms: int | None) -> str:
    if not ms:
        return ""
    return datetime.fromtimestamp(ms / 1000).strftime("%Y-%m-%d")


async def hotmart_product_catalog_app() -> PrefabApp:
    """Catálogo de produtos — visão geral com formato/status/preço/info.

    Cards de metrics + PieChart status + DataTable. Use pra 'lista de
    produtos', 'catálogo', 'meus produtos ativos'.
    """
    client = get_client()
    res = await client.get("/products/api/v1/products", params={"max_results": 100})
    items = res.get("items", []) if isinstance(res, dict) else []

    by_format: Counter[str] = Counter()
    by_status: Counter[str] = Counter()
    for it in items:
        by_format[it.get("format") or "?"] += 1
        by_status[it.get("status") or "?"] += 1

    fmt_data = [{"name": k, "value": v} for k, v in by_format.most_common()]

    rows = []
    for it in items[:200]:
        rows.append({
            "id": it.get("id"),
            "name": it.get("name") or "?",
            "format": it.get("format") or "?",
            "status": it.get("status") or "?",
            "created": _epoch_ms_to_date(it.get("created_at")),
        })

    with PrefabApp() as app:
        with Column(gap=4, css_class="p-6"):
            Heading(content="Catálogo de Produtos")

            with Grid(columns=[1, 1, 1], gap=4):
                with Card():
                    with CardHeader():
                        CardTitle(content="Total")
                    with CardContent():
                        Metric(label="Produtos", value=str(len(items)))
                with Card():
                    with CardHeader():
                        CardTitle(content="Ativos")
                    with CardContent():
                        Metric(label="Ativos", value=str(by_status.get("ACTIVE", 0)))
                with Card():
                    with CardHeader():
                        CardTitle(content="Pausados")
                    with CardContent():
                        Metric(label="Pausados", value=str(by_status.get("PAUSED", 0)))

            with Card():
                with CardHeader():
                    CardTitle(content="Por formato")
                with CardContent():
                    PieChart(data=fmt_data, data_key="value", name_key="name")

            with Card():
                with CardHeader():
                    CardTitle(content=f"Produtos ({len(items)})")
                with CardContent():
                    DataTable(
                        columns=[
                            DataTableColumn(key="id", header="ID"),
                            DataTableColumn(key="name", header="Nome", sortable=True),
                            DataTableColumn(key="format", header="Formato", sortable=True),
                            DataTableColumn(key="status", header="Status", sortable=True),
                            DataTableColumn(key="created", header="Criado em", sortable=True),
                        ],
                        rows=rows,
                        search=True,
                    )
    return app


async def hotmart_coupon_manager_app(product_id: int) -> PrefabApp:
    """Painel de cupons de um produto — listagem com validade/desconto/usos.

    DataTable de cupons + Metric. Use pra 'listar cupons do produto X',
    'ver cupons ativos', 'gerenciar cupons'. Pra CRIAR cupom use a tool
    `hotmart_coupon_create` direta.

    Args:
        product_id: Product ID.
    """
    client = get_client()
    res = await client.get(f"/products/api/v1/coupon/product/{product_id}")
    items = res.get("items", []) if isinstance(res, dict) else []

    rows = []
    for c in items[:200]:
        rows.append({
            "code": c.get("code") or "?",
            "discount": f"{(c.get('discount', 0) or 0) * 100:.1f}%",
            "start": _epoch_ms_to_date(c.get("start_date")),
            "end": _epoch_ms_to_date(c.get("end_date")),
            "uses": c.get("number_of_uses_made", 0),
            "max_uses": c.get("max_number_of_uses_per_user") or "—",
            "status": c.get("status") or "?",
        })

    with PrefabApp() as app:
        with Column(gap=4, css_class="p-6"):
            Heading(content=f"Cupons — Produto {product_id}")

            with Grid(columns=[1, 1], gap=4):
                with Card():
                    with CardHeader():
                        CardTitle(content="Total de cupons")
                    with CardContent():
                        Metric(label="Cupons", value=str(len(items)))
                with Card():
                    with CardHeader():
                        CardTitle(content="Usos totais")
                    with CardContent():
                        Metric(
                            label="Usos",
                            value=str(sum(c.get("number_of_uses_made", 0) or 0 for c in items)),
                        )

            with Card():
                with CardHeader():
                    CardTitle(content="Cupons cadastrados")
                with CardContent():
                    DataTable(
                        columns=[
                            DataTableColumn(key="code", header="Código", sortable=True),
                            DataTableColumn(key="discount", header="Desconto", sortable=True),
                            DataTableColumn(key="start", header="Início", sortable=True),
                            DataTableColumn(key="end", header="Fim", sortable=True),
                            DataTableColumn(key="uses", header="Usos", sortable=True),
                            DataTableColumn(key="max_uses", header="Max/User"),
                            DataTableColumn(key="status", header="Status", sortable=True),
                        ],
                        rows=rows,
                        search=True,
                    )
    return app


__all__ = ["hotmart_product_catalog_app", "hotmart_coupon_manager_app"]
