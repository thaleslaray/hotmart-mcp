"""Event ticketing dashboards — Prefab UI apps."""
from __future__ import annotations

from collections import Counter
from datetime import datetime

from prefab_ui import PrefabApp
from prefab_ui.components import (
    Card, CardContent, CardHeader, CardTitle, Column, DataTable,
    DataTableColumn, Grid, Heading, Metric,
)
from prefab_ui.components.charts import PieChart

from hotmart_mcp._shared import get_client


def _epoch_ms_to_date(ms: int | None) -> str:
    if not ms:
        return ""
    return datetime.fromtimestamp(ms / 1000).strftime("%Y-%m-%d %H:%M")


async def hotmart_event_dashboard_app(event_id: int) -> PrefabApp:
    """Painel de evento — info + lista de participantes + breakdown lotes.

    Card com info + DataTable participantes + PieChart por lote. Use pra
    'ver dados do evento X', 'quem comprou ingresso pro evento'. Funciona
    apenas pra produtos formato ETICKET (não ONLINE_EVENT).

    Args:
        event_id: Event ID (integer).
    """
    client = get_client()
    info = await client.get(f"/events/api/v1/{event_id}/info")
    parts_res = await client.get(
        f"/events/api/v1/{event_id}/participants",
        params={"max_results": 200},
    )
    participants = parts_res.get("items", []) if isinstance(parts_res, dict) else []

    product = info.get("product", {}) if isinstance(info, dict) else {}
    lots = info.get("lots", []) if isinstance(info, dict) else []

    by_lot: Counter[str] = Counter()
    rows = []
    for p in participants:
        buyer = p.get("buyer", {}) or {}
        prod = p.get("product", {}) or {}
        lot = p.get("lot", {}) or {}
        eticket = p.get("eticket", {}) or {}
        participant = p.get("participant", {}) or {}
        by_lot[lot.get("name") or "?"] += 1
        rows.append({
            "ticket": eticket.get("code") or "?",
            "participant": participant.get("name") or buyer.get("name") or "?",
            "email": participant.get("email") or buyer.get("email") or "",
            "buyer": buyer.get("name") or "?",
            "product": prod.get("name") or "?",
            "lot": lot.get("name") or "?",
        })

    lot_data = [{"name": k, "value": v} for k, v in by_lot.most_common()]

    with PrefabApp() as app:
        with Column(gap=4, css_class="p-6"):
            Heading(content=f"Evento {event_id} — {product.get('name', '?')}")

            with Grid(columns=[1, 1, 1], gap=4):
                with Card():
                    with CardHeader():
                        CardTitle(content="Participantes")
                    with CardContent():
                        Metric(label="Total", value=str(len(participants)))
                with Card():
                    with CardHeader():
                        CardTitle(content="Início")
                    with CardContent():
                        Metric(
                            label="Data",
                            value=_epoch_ms_to_date(info.get("start_event_date")) if isinstance(info, dict) else "—",
                        )
                with Card():
                    with CardHeader():
                        CardTitle(content="Lotes")
                    with CardContent():
                        Metric(label="Lotes", value=str(len(lots)))

            with Card():
                with CardHeader():
                    CardTitle(content="Por lote")
                with CardContent():
                    PieChart(data=lot_data, data_key="value", name_key="name")

            with Card():
                with CardHeader():
                    CardTitle(content=f"Participantes ({len(participants)})")
                with CardContent():
                    DataTable(
                        columns=[
                            DataTableColumn(key="ticket", header="Ticket"),
                            DataTableColumn(key="participant", header="Participante", sortable=True),
                            DataTableColumn(key="email", header="Email"),
                            DataTableColumn(key="buyer", header="Comprador", sortable=True),
                            DataTableColumn(key="product", header="Produto"),
                            DataTableColumn(key="lot", header="Lote", sortable=True),
                        ],
                        rows=rows,
                        search=True,
                    )
    return app


__all__ = ["hotmart_event_dashboard_app"]
