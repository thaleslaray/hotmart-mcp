"""Auto-generated Hotmart API tools — coupons."""

import json
from typing import Optional

from hotmart_mcp._shared import get_client

__all__ = ["create_coupon", "get_coupons", "delete_coupon"]


async def create_coupon(
    product_id: int,
    code: str,
    discount: float,
    start_date: Optional[int] = None,
    end_date: Optional[int] = None,
    affiliate: Optional[int] = None,
    offer_ids: Optional[list[int]] = None,
) -> str:
    """Create Coupon
    
    Cria um cupom de desconto para um produto.
    
    Args:
        product_id: ID do produto
        code: Código do cupom (máximo 25 caracteres)
        discount: Percentual de desconto (entre 0 e 0.99, exclusivo)
        start_date: Data de início de validade (timestamp em milissegundos)
        end_date: Data de fim de validade (timestamp em milissegundos)
        affiliate: ID do afiliado
        offer_ids: IDs das ofertas aplicáveis"""
    endpoint = f"/products/api/v1/product/{product_id}/coupon"
    body = {}
    body["code"] = code
    body["discount"] = discount
    if start_date is not None:
        body["start_date"] = start_date
    if end_date is not None:
        body["end_date"] = end_date
    if affiliate is not None:
        body["affiliate"] = affiliate
    if offer_ids is not None:
        body["offer_ids"] = offer_ids
    result = await get_client().post(endpoint, json=body)
    return json.dumps(result, indent=2)


async def get_coupons(
    product_id: int,
    code: Optional[str] = None,
    page_token: Optional[str] = None,
    select: Optional[str] = None,
) -> str:
    """Get Coupons
    
    Retorna os cupons de um produto.
    
    Args:
        product_id: ID do produto
        code: Código do cupom
        page_token: Token de paginação para a próxima página
        select: Seleção de campos customizados na resposta"""
    endpoint = f"/products/api/v1/coupon/product/{product_id}"
    params = {}
    if code is not None:
        params["code"] = code
    if page_token is not None:
        params["page_token"] = page_token
    if select is not None:
        params["select"] = select
    result = await get_client().get(endpoint, params=params)
    return json.dumps(result, indent=2)


async def delete_coupon(
    coupon_id: int,
) -> str:
    """Delete Coupon
    
    Exclui um cupom de desconto.
    
    Args:
        coupon_id: ID do cupom"""
    endpoint = f"/products/api/v1/coupon/{coupon_id}"
    result = await get_client().delete(endpoint)
    return json.dumps(result, indent=2)
