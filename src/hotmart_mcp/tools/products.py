"""Auto-generated Hotmart API tools — products."""

import json
from typing import Optional

from hotmart_mcp._shared import get_client

__all__ = ["list_products", "get_product_offers", "get_product_plans"]


async def list_products(
    max_results: Optional[int] = None,
    page_token: Optional[str] = None,
    id_: Optional[int] = None,
    status: Optional[str] = None,
    format_: Optional[str] = None,
    select: Optional[str] = None,
) -> str:
    """List Products
    
    Retorna a lista de produtos.
    
    Args:
        max_results: Número máximo de resultados por página
        page_token: Token de paginação para a próxima página
        id_: ID do produto
        status: Status do produto.
        Valores aceitos (case-sensitive, passe EXATAMENTE como abaixo):
          - `DRAFT`
          - `ACTIVE`
          - `PAUSED`
          - `NOT_APPROVED`
          - `IN_REVIEW`
          - `DELETED`
          - `CHANGES_PENDING_ON_PRODUCT`
        format_: Formato do produto.
        Valores aceitos (case-sensitive, passe EXATAMENTE como abaixo):
          - `EBOOK`
          - `SOFTWARE`
          - `MOBILE_APPS`
          - `VIDEOS`
          - `AUDIOS`
          - `TEMPLATES`
          - `IMAGES`
          - `ONLINE_COURSE`
          - `SERIAL_CODES`
          - `ETICKET`
          - `ONLINE_SERVICE`
          - `ONLINE_EVENT`
          - `BUNDLE`
          - `COMMUNITY`
        select: Seleção de campos customizados na resposta"""
    endpoint = "/products/api/v1/products"
    params = {}
    if max_results is not None:
        params["max_results"] = max_results
    if page_token is not None:
        params["page_token"] = page_token
    if id_ is not None:
        params["id"] = id_
    if status is not None:
        params["status"] = status
    if format_ is not None:
        params["format"] = format_
    if select is not None:
        params["select"] = select
    result = await get_client().get(endpoint, params=params)
    return json.dumps(result, indent=2)


async def get_product_offers(
    product_id: int,
    max_results: Optional[int] = None,
    page_token: Optional[str] = None,
    offer_key: Optional[str] = None,
    select: Optional[str] = None,
) -> str:
    """Get Product Offers
    
    Retorna as ofertas de um produto.
    
    Args:
        product_id: ID do produto
        max_results: Número máximo de resultados por página
        page_token: Token de paginação para a próxima página
        offer_key: Chave da oferta
        select: Seleção de campos customizados na resposta"""
    endpoint = f"/products/api/v1/product/{product_id}/offers"
    params = {}
    if max_results is not None:
        params["max_results"] = max_results
    if page_token is not None:
        params["page_token"] = page_token
    if offer_key is not None:
        params["offer_key"] = offer_key
    if select is not None:
        params["select"] = select
    result = await get_client().get(endpoint, params=params)
    return json.dumps(result, indent=2)


async def get_product_plans(
    product_id: int,
    max_results: Optional[int] = None,
    page_token: Optional[str] = None,
    id_: Optional[int] = None,
    select: Optional[str] = None,
) -> str:
    """Get Product Plans
    
    Retorna os planos de assinatura de um produto.
    
    Args:
        product_id: ID do produto
        max_results: Número máximo de resultados por página
        page_token: Token de paginação para a próxima página
        id_: ID do plano
        select: Seleção de campos customizados na resposta"""
    endpoint = f"/products/api/v1/product/{product_id}/plans"
    params = {}
    if max_results is not None:
        params["max_results"] = max_results
    if page_token is not None:
        params["page_token"] = page_token
    if id_ is not None:
        params["id"] = id_
    if select is not None:
        params["select"] = select
    result = await get_client().get(endpoint, params=params)
    return json.dumps(result, indent=2)
