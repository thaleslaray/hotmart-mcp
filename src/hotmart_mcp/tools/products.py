"""Auto-generated Hotmart API tools — products."""

import json
from typing import Optional

from hotmart_mcp._shared import get_client

__all__ = ["hotmart_products_list", "hotmart_product_offers_list", "hotmart_product_plans_list"]


async def hotmart_products_list(
    max_results: Optional[int] = None,
    page_token: Optional[str] = None,
    id_: Optional[int] = None,
    status: Optional[str] = None,
    format_: Optional[str] = None,
    select: Optional[str] = None,
) -> str:
    """List Products. Example: hotmart_products_list(max_results=10).
    
    Args:
        max_results: Max results per page
        page_token: Pagination token for the next page
        id_: Product ID
        status: Status do produto.
        Allowed values (case-sensitive, pass EXACTLY as listed):
          - `DRAFT`
          - `ACTIVE`
          - `PAUSED`
          - `NOT_APPROVED`
          - `IN_REVIEW`
          - `DELETED`
          - `CHANGES_PENDING_ON_PRODUCT`
        format_: Formato do produto.
        Allowed values (case-sensitive, pass EXACTLY as listed):
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
        select: Custom field selection in response"""
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


async def hotmart_product_offers_list(
    product_id: int,
    max_results: Optional[int] = None,
    page_token: Optional[str] = None,
    offer_key: Optional[str] = None,
    select: Optional[str] = None,
) -> str:
    """Get Product Offers. Example: hotmart_product_offers_list(product_id=12345, max_results=10).
    
    Args:
        product_id: Product ID
        max_results: Max results per page
        page_token: Pagination token for the next page
        offer_key: Offer key
        select: Custom field selection in response"""
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


async def hotmart_product_plans_list(
    product_id: int,
    max_results: Optional[int] = None,
    page_token: Optional[str] = None,
    id_: Optional[int] = None,
    select: Optional[str] = None,
) -> str:
    """Get Product Plans. Example: hotmart_product_plans_list(product_id=12345, max_results=10).
    
    Args:
        product_id: Product ID
        max_results: Max results per page
        page_token: Pagination token for the next page
        id_: ID do plano
        select: Custom field selection in response"""
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
