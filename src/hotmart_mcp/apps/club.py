"""Club (members area) dashboards — Prefab UI apps."""
from __future__ import annotations

from collections import Counter
from typing import Optional

from prefab_ui import PrefabApp
from prefab_ui.components import (
    Card, CardContent, CardHeader, CardTitle, Column, DataTable,
    DataTableColumn, Grid, Heading, Metric, Progress,
)
from prefab_ui.components.charts import BarChart, ChartSeries, PieChart

from hotmart_mcp._shared import get_client


async def hotmart_students_overview_app(subdomain: str) -> PrefabApp:
    """Visão geral dos alunos na área de membros — counts + ranking de progresso.

    Cards de metrics (total, ativos, completos) + PieChart engagement +
    DataTable com progresso. Use pra 'lista de alunos', 'progresso médio',
    'quantos alunos completaram'.

    Args:
        subdomain: Members area subdomain (the slug from `hotmart.com/club/<slug>`).
    """
    client = get_client()
    res = await client.get("/club/api/v1/users", params={"subdomain": subdomain})
    items = res.get("items", []) if isinstance(res, dict) else []

    total = len(items)
    by_status: Counter[str] = Counter()
    by_engagement: Counter[str] = Counter()

    rows = []
    for u in items[:200]:
        progress = u.get("progress", {}) or {}
        pct = progress.get("completed_percentage") or 0
        by_status[u.get("status") or "?"] += 1
        by_engagement[u.get("engagement") or "?"] += 1
        rows.append({
            "name": u.get("name") or "?",
            "email": u.get("email") or "",
            "status": u.get("status") or "?",
            "engagement": u.get("engagement") or "?",
            "progress_pct": f"{pct}%",
            "completed": f"{progress.get('completed', 0)}/{progress.get('total', 0)}",
        })

    rows.sort(key=lambda r: int(r["progress_pct"].rstrip("%")), reverse=True)

    engagement_data = [{"name": k, "value": v} for k, v in by_engagement.most_common()]

    with PrefabApp() as app:
        with Column(gap=4, css_class="p-6"):
            Heading(content=f"Alunos — {subdomain}")

            with Grid(columns=[1, 1, 1], gap=4):
                with Card():
                    with CardHeader():
                        CardTitle(content="Total de alunos")
                    with CardContent():
                        Metric(label="Total", value=str(total))
                with Card():
                    with CardHeader():
                        CardTitle(content="Ativos")
                    with CardContent():
                        Metric(label="Ativos", value=str(by_status.get("ACTIVE", 0)))
                with Card():
                    with CardHeader():
                        CardTitle(content="Bloqueados")
                    with CardContent():
                        Metric(label="Bloqueados", value=str(by_status.get("BLOCKED", 0)))

            with Card():
                with CardHeader():
                    CardTitle(content="Engajamento")
                with CardContent():
                    PieChart(data=engagement_data, data_key="value", name_key="name")

            with Card():
                with CardHeader():
                    CardTitle(content=f"Ranking de progresso (top {len(rows)})")
                with CardContent():
                    DataTable(
                        columns=[
                            DataTableColumn(key="name", header="Aluno", sortable=True),
                            DataTableColumn(key="email", header="Email"),
                            DataTableColumn(key="status", header="Status", sortable=True),
                            DataTableColumn(key="engagement", header="Engajamento", sortable=True),
                            DataTableColumn(key="progress_pct", header="Progresso", sortable=True),
                            DataTableColumn(key="completed", header="Aulas"),
                        ],
                        rows=rows,
                        search=True,
                    )
    return app


async def hotmart_module_analytics_app(subdomain: str) -> PrefabApp:
    """Análise por módulo da área de membros — qty aulas + drill-down possível.

    BarChart de aulas por módulo + DataTable. Use pra 'estrutura da área
    de membros', 'quantas aulas por módulo'.

    Args:
        subdomain: Members area subdomain.
    """
    client = get_client()
    res = await client.get("/club/api/v1/modules", params={"subdomain": subdomain})
    modules = res.get("items", []) if isinstance(res, dict) else []

    # Pra cada módulo, busca pages (limitado pra não bater rate-limit)
    enriched = []
    for m in modules[:50]:
        mid = m.get("id")
        page_count = 0
        if mid:
            try:
                pages_res = await client.get(
                    f"/club/api/v1/modules/{mid}/pages",
                    params={"subdomain": subdomain},
                )
                pages = pages_res.get("items", []) if isinstance(pages_res, dict) else []
                page_count = len(pages)
            except Exception:
                pass
        enriched.append({
            "id": mid,
            "name": m.get("name") or "?",
            "is_extra": "Sim" if m.get("is_extra") else "Não",
            "pages": page_count,
        })

    chart_data = sorted(enriched, key=lambda x: x["pages"], reverse=True)[:15]

    with PrefabApp() as app:
        with Column(gap=4, css_class="p-6"):
            Heading(content=f"Módulos — {subdomain}")

            with Grid(columns=[1, 1], gap=4):
                with Card():
                    with CardHeader():
                        CardTitle(content="Total de módulos")
                    with CardContent():
                        Metric(label="Módulos", value=str(len(modules)))
                with Card():
                    with CardHeader():
                        CardTitle(content="Total de aulas")
                    with CardContent():
                        Metric(label="Aulas", value=str(sum(m["pages"] for m in enriched)))

            with Card():
                with CardHeader():
                    CardTitle(content="Aulas por módulo (top 15)")
                with CardContent():
                    BarChart(
                        data=chart_data,
                        series=[ChartSeries(data_key="pages", label="Aulas")],
                        x_axis="name",
                    )

            with Card():
                with CardHeader():
                    CardTitle(content="Módulos")
                with CardContent():
                    DataTable(
                        columns=[
                            DataTableColumn(key="id", header="ID"),
                            DataTableColumn(key="name", header="Nome", sortable=True),
                            DataTableColumn(key="is_extra", header="Extra"),
                            DataTableColumn(key="pages", header="Aulas", sortable=True),
                        ],
                        rows=enriched,
                        search=True,
                    )
    return app


__all__ = ["hotmart_students_overview_app", "hotmart_module_analytics_app"]
