"""Auto-generated Hotmart API tools — negotiation."""

import json
from typing import Optional

from hotmart_mcp._shared import get_client

__all__ = ["generate_negotiation"]


async def generate_negotiation(
    subscription_id: int,
    recurrences: list[int],
    payment_type: str,
    discount: Optional[dict] = None,
    document: Optional[str] = None,
) -> str:
    """Generate Negotiation
    
    Gera boleto ou PIX para parcelas de assinatura em atraso.
    
    Args:
        subscription_id: ID da assinatura
        recurrences: Números das recorrências em atraso (1 a 5 valores)
        payment_type: Tipo de pagamento para a negociação. Valores aceitos: 'BOLETO', 'PIX'
        discount: discount
        document: CPF ou CNPJ do assinante (obrigatório para BOLETO)"""
    endpoint = "/payments/api/v1/installments/negotiate"
    body = {}
    body["subscription_id"] = subscription_id
    body["recurrences"] = recurrences
    body["payment_type"] = payment_type
    if discount is not None:
        body["discount"] = discount
    if document is not None:
        body["document"] = document
    result = await get_client().post(endpoint, json=body)
    return json.dumps(result, indent=2)
