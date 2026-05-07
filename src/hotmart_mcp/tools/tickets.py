"""Auto-generated Hotmart API tools — tickets."""

import json
from typing import Optional

from hotmart_mcp._shared import get_client

__all__ = ["get_event_info", "get_event_participants"]


async def get_event_info(
    event_id: int,
    select: Optional[str] = None,
) -> str:
    """Event Info
    
    Retorna informações de um evento.
    
    Args:
        event_id: ID do evento
        select: Seleção de campos customizados na resposta"""
    endpoint = f"/events/api/v1/{event_id}/info"
    params = {}
    if select is not None:
        params["select"] = select
    result = await get_client().get(endpoint, params=params)
    return json.dumps(result, indent=2)


async def get_event_participants(
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
    """Event Participants
    
    Retorna os participantes de um evento.
    
    Args:
        event_id: ID do evento
        max_results: Número máximo de resultados por página
        page_token: Token de paginação para a próxima página
        buyer_email: E-mail do comprador
        participant_email: E-mail do participante
        last_update: Última atualização (timestamp em milissegundos)
        id_lot: ID do lote
        ticket_status: Status do ingresso. Values: SOLD, INVITE, INVITE_CANCELED, REFUNDED, CHARGEBACK, EXCLUDED, AVAILABLE, RESERVED
        ticket_type: Tipo do ingresso. Values: PAID, FREE, ALL
        checkin_status: Status do check-in. Values: PENDING, PARTIAL, CONCLUDED, ALL
        id_eticket: ID do e-ticket
        ticket_qr_code: QR code do ingresso
        select: Seleção de campos customizados na resposta"""
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
