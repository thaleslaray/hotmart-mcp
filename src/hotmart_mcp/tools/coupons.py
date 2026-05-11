"""Auto-generated Hotmart API tools — coupons."""

import json
from typing import Optional

from hotmart_mcp._shared import get_client

__all__ = ["hotmart_coupon_create", "hotmart_coupons_list", "hotmart_coupon_delete"]


async def hotmart_coupon_create(
    product_id: int,
    code: str,
    discount: float,
    start_date: Optional[int] = None,
    end_date: Optional[int] = None,
    affiliate: Optional[int] = None,
    offer_ids: Optional[list[int]] = None,
) -> str:
    """Create Coupon. Example: hotmart_coupon_create(product_id=12345).
    
    Args:
        product_id: Product ID
        code: Coupon code (máximo 25 caracteres)
        discount: Discount fraction (between 0 and 0.99 exclusive). **Fraction between 0 and 1** (NOT percent). Ex: `0.25` = 25% off. Pass `0.10` for 10%, NOT `10`.
        start_date: Validity start date. Unix timestamp in **milliseconds** (not seconds, not ISO). Ex: `1730419200000` = 2024-11-01 00:00 UTC. Python: `int(datetime(2024,11,1).timestamp() * 1000)`.
        end_date: Data de fim de validade. Unix timestamp in **milliseconds** (not seconds, not ISO). Ex: `1730419200000` = 2024-11-01 00:00 UTC. Python: `int(datetime(2024,11,1).timestamp() * 1000)`.
        affiliate: ID do afiliado
        offer_ids: IDs das ofertas aplicáveis. Pass a JSON array of integers, e.g. `[12345, 67890]`."""
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


async def hotmart_coupons_list(
    product_id: int,
    code: Optional[str] = None,
    page_token: Optional[str] = None,
    select: Optional[str] = None,
) -> str:
    """Get Coupons. Example: hotmart_coupons_list(product_id=12345).
    
    Args:
        product_id: Product ID
        code: Coupon code
        page_token: Pagination token for the next page
        select: Custom field selection in response"""
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


async def hotmart_coupon_delete(
    coupon_id: int,
) -> str:
    """Delete Coupon. Example: hotmart_coupon_delete(coupon_id=12345).
    
    Args:
        coupon_id: Coupon ID"""
    endpoint = f"/products/api/v1/coupon/{coupon_id}"
    result = await get_client().delete(endpoint)
    return json.dumps(result, indent=2)
