"""Auto-generated Hotmart API tools — tickets."""

import json
from typing import Optional

from hotmart_mcp._shared import get_client

__all__ = ["hotmart_event_info_get", "hotmart_event_participants_list"]


async def hotmart_event_info_get(
    event_id: int,
    select: Optional[str] = None,
) -> str:
    """Event Info. Example: hotmart_event_info_get(event_id=12345).
    
    Args:
        event_id: Event ID
        select: Custom field selection in response"""
    endpoint = f"/events/api/v1/{event_id}/info"
    params = {}
    if select is not None:
        params["select"] = select
    result = await get_client().get(endpoint, params=params)
    return json.dumps(result, indent=2)


async def hotmart_event_participants_list(
    event_id: int,
    max_results: Optional[int] = None,
    page_token: Optional[str] = None,
    buyer_email: Optional[str] = None,
    participant_email: Optional[str] = None,
    last_update: Optional[int] = None,
    id_lot: Optional[int] = None,
    ticket_status: Optional[str] = None,
    ticket_type: Optional[str] = None,
    checkin_status: Optional[str] = None,
    id_eticket: Optional[int] = None,
    ticket_qr_code: Optional[str] = None,
    select: Optional[str] = None,
) -> str:
    """Event Participants. Example: hotmart_event_participants_list(event_id=12345, max_results=10).
    
    Args:
        event_id: Event ID
        max_results: Max results per page
        page_token: Pagination token for the next page
        buyer_email: Buyer email
        participant_email: Email do participante
        last_update: Última atualização. Unix timestamp in **milliseconds** (not seconds, not ISO). Ex: `1730419200000` = 2024-11-01 00:00 UTC. Python: `int(datetime(2024,11,1).timestamp() * 1000)`.
        id_lot: ID do lote
        ticket_status: Status do ingresso.
        Allowed values (case-sensitive, pass EXACTLY as listed):
          - `SOLD`
          - `INVITE`
          - `INVITE_CANCELED`
          - `REFUNDED`
          - `CHARGEBACK`
          - `EXCLUDED`
          - `AVAILABLE`
          - `RESERVED`
        ticket_type: Tipo do ingresso. Allowed values: 'PAID', 'FREE', 'ALL'
        checkin_status: Status do check-in.
        Allowed values (case-sensitive, pass EXACTLY as listed):
          - `PENDING`
          - `PARTIAL`
          - `CONCLUDED`
          - `ALL`
        id_eticket: ID do e-ticket
        ticket_qr_code: QR code do ingresso. Format: alphanumeric Hotmart code (ex: `H123A4B5`, not UUID, not int)
        select: Custom field selection in response"""
    endpoint = f"/events/api/v1/{event_id}/participants"
    params = {}
    if max_results is not None:
        params["max_results"] = max_results
    if page_token is not None:
        params["page_token"] = page_token
    if buyer_email is not None:
        params["buyer_email"] = buyer_email
    if participant_email is not None:
        params["participant_email"] = participant_email
    if last_update is not None:
        params["last_update"] = last_update
    if id_lot is not None:
        params["id_lot"] = id_lot
    if ticket_status is not None:
        params["ticket_status"] = ticket_status
    if ticket_type is not None:
        params["ticket_type"] = ticket_type
    if checkin_status is not None:
        params["checkin_status"] = checkin_status
    if id_eticket is not None:
        params["id_eticket"] = id_eticket
    if ticket_qr_code is not None:
        params["ticket_qr_code"] = ticket_qr_code
    if select is not None:
        params["select"] = select
    result = await get_client().get(endpoint, params=params)
    return json.dumps(result, indent=2)
