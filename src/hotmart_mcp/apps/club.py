"""Club (members area) dashboards — Prefab UI apps (schema-validated)."""
from __future__ import annotations

from collections import Counter

from prefab_ui import PrefabApp
from prefab_ui.components import (
    Card, CardContent, CardHeader, CardTitle, Column, DataTable,
    DataTableColumn, Grid, Heading, Metric,
)
from prefab_ui.components.charts import BarChart, ChartSeries, PieChart

from hotmart_mcp._shared import get_client
from hotmart_mcp.models import Module, Student
from hotmart_mcp.apps._helpers import parse_items


async def hotmart_students_overview_app(subdomain: str) -> PrefabApp:
    """Visão geral dos alunos na área de membros — counts + progresso.

    Cards (total, ativos, bloqueados) + PieChart engajamento + DataTable
    ranking. Use pra 'lista de alunos', 'progresso médio', 'quantos
    alunos completaram'.

    Args:
        subdomain: Members area subdomain (slug de `hotmart.com/club/<slug>`).
    """
    client = get_client()
    raw = await client.get("/club/api/v1/users", params={"subdomain": subdomain})
    students: list[Student] = parse_items(raw, Student)

    total = len(students)
    by_status: Counter[str] = Counter()
    by_engagement: Counter[str] = Counter()

    rows = []
    for s in students[:200]:
        pct = (s.progress.completed_percentage if s.progress else None) or 0
        completed = (s.progress.completed if s.progress else None) or 0
        progress_total = (s.progress.total if s.progress else None) or 0
        by_status[(s.status if s.status else None) or "?"] += 1
        by_engagement[(s.engagement if s.engagement else None) or "?"] += 1
        rows.append({
            "name": s.name or "?",
            "email": s.email or "",
            "status": (s.status if s.status else None) or "?",
            "engagement": (s.engagement if s.engagement else None) or "?",
            "progress_pct": f"{pct:.0f}%",
            "completed": f"{completed}/{progress_total}",
            "_pct": pct,
        })

    rows.sort(key=lambda r: r["_pct"], reverse=True)
    for r in rows: r.pop("_pct", None)

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
    """Análise por módulo da área de membros — qty aulas por módulo.

    BarChart aulas/módulo + DataTable. Use pra 'estrutura da área de
    membros', 'quantas aulas por módulo'.

    Args:
        subdomain: Members area subdomain.
    """
    client = get_client()
    raw = await client.get("/club/api/v1/modules", params={"subdomain": subdomain})
    modules: list[Module] = parse_items(raw, Module)

    enriched = [
        {
            "id": m.module_id or "?",
            "name": m.name or "?",
            "is_extra": "Sim" if m.is_extra else "Não",
            "pages": m.total_pages or 0,
        }
        for m in modules
    ]

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
