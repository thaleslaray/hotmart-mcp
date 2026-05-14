"""Event ticketing dashboards — Prefab UI apps (schema-validated)."""
from __future__ import annotations

from collections import Counter

from prefab_ui import PrefabApp
from prefab_ui.components import (
    Card, CardContent, CardHeader, CardTitle, Column, DataTable,
    DataTableColumn, Grid, Heading, Metric,
)
from prefab_ui.components.charts import PieChart

from hotmart_mcp._shared import get_client
from hotmart_mcp.models import EventInfo, EventParticipant
from hotmart_mcp.apps._helpers import epoch_ms_to_date, parse_items


async def hotmart_event_dashboard_app(event_id: int) -> PrefabApp:
    """Painel de evento — info + lista de participantes + breakdown lotes.

    Card com info + DataTable participantes + PieChart por lote. Funciona
    apenas pra produtos formato ETICKET (não ONLINE_EVENT). Use pra 'ver
    dados do evento X', 'quem comprou ingresso pro evento'.

    Args:
        event_id: Event ID (integer).
    """
    client = get_client()
    raw_info = await client.get(f"/events/api/v1/{event_id}/info")
    raw_parts = await client.get(
        f"/events/api/v1/{event_id}/participants",
        params={"max_results": 200},
    )

    info = EventInfo.model_validate(raw_info) if isinstance(raw_info, dict) else EventInfo()
    participants: list[EventParticipant] = parse_items(raw_parts, EventParticipant)

    by_lot: Counter[str] = Counter()
    rows = []
    for p in participants:
        lot_name = (p.lot.name if p.lot else None) or "?"
        by_lot[lot_name] += 1
        rows.append({
            "ticket": str(p.eticket.id) if p.eticket and p.eticket.id else "?",
            "participant": (p.participant.name if p.participant else None)
                           or (p.buyer.name if p.buyer else None) or "?",
            "email": (p.participant.email if p.participant else None)
                     or (p.buyer.email if p.buyer else None) or "",
            "buyer": (p.buyer.name if p.buyer else None) or "?",
            "product": (p.product.name if p.product else None) or "?",
            "lot": lot_name,
            "status": (p.eticket.ticket_status if p.eticket and p.eticket.ticket_status else "—"),
        })

    lot_data = [{"name": k, "value": v} for k, v in by_lot.most_common()]
    event_name = (info.product.name if info.product else None) or "?"

    with PrefabApp() as app:
        with Column(gap=4, css_class="p-6"):
            Heading(content=f"Evento {event_id} — {event_name}")

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
                        Metric(label="Data", value=epoch_ms_to_date(info.start_event_date) or "—")
                with Card():
                    with CardHeader():
                        CardTitle(content="Lotes")
                    with CardContent():
                        Metric(label="Lotes", value=str(len(info.lots or [])))

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
                            DataTableColumn(key="status", header="Status", sortable=True),
                        ],
                        rows=rows,
                        search=True,
                    )
    return app


__all__ = ["hotmart_event_dashboard_app"]
