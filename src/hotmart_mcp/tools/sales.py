"""Auto-generated Hotmart API tools — sales."""

import json
from typing import Optional

from hotmart_mcp._shared import get_client

__all__ = ["hotmart_sales_history_list", "hotmart_sales_summary_list", "hotmart_sales_participants_list", "hotmart_sales_commissions_list", "hotmart_sales_price_details_list", "hotmart_sale_refund"]


async def hotmart_sales_history_list(
    max_results: Optional[int] = None,
    page_token: Optional[str] = None,
    product_id: Optional[int] = None,
    start_date: Optional[int] = None,
    end_date: Optional[int] = None,
    sales_source: Optional[str] = None,
    transaction: Optional[str] = None,
    select: Optional[str] = None,
    buyer_name: Optional[str] = None,
    buyer_email: Optional[str] = None,
    offer_code: Optional[str] = None,
    commission_as: Optional[str] = None,
    transaction_status: Optional[str] = None,
    payment_type: Optional[str] = None,
) -> str:
    """Sales History. Example: hotmart_sales_history_list(max_results=10). Don't use this for aggregated metrics — use `hotmart_sales_summary_list` for totals/counts.
    
    Args:
        max_results: Max results per page
        page_token: Pagination token for the next page
        product_id: Product ID
        start_date: Start date. Unix timestamp in **milliseconds** (not seconds, not ISO). Ex: `1730419200000` = 2024-11-01 00:00 UTC. Python: `int(datetime(2024,11,1).timestamp() * 1000)`.
        end_date: End date. Unix timestamp in **milliseconds** (not seconds, not ISO). Ex: `1730419200000` = 2024-11-01 00:00 UTC. Python: `int(datetime(2024,11,1).timestamp() * 1000)`.
        sales_source: Sale source
        transaction: Transaction code
        select: Custom field selection in response
        buyer_name: Buyer name
        buyer_email: Buyer email
        offer_code: Offer code. Format: alphanumeric Hotmart code (ex: `H123A4B5`, not UUID, not int)
        commission_as: Authenticated user's commission role. Allowed values: 'PRODUCER', 'COPRODUCER', 'AFFILIATE'
        transaction_status: Transaction status.
        Allowed values (case-sensitive, pass EXACTLY as listed):
          - `APPROVED`
          - `BLOCKED`
          - `CANCELLED`
          - `CHARGEBACK`
          - `COMPLETE`
          - `EXPIRED`
          - `NO_FUNDS`
          - `OVERDUE`
          - `PARTIALLY_REFUNDED`
          - `PRE_ORDER`
          - `PRINTED_BILLET`
          - `PROCESSING_TRANSACTION`
          - `PROTESTED`
          - `REFUNDED`
          - `STARTED`
          - `UNDER_ANALISYS`
          - `WAITING_PAYMENT`
        payment_type: Payment type.
        Allowed values (case-sensitive, pass EXACTLY as listed):
          - `BILLET`
          - `CASH_PAYMENT`
          - `CREDIT_CARD`
          - `DIRECT_BANK_TRANSFER`
          - `DIRECT_DEBIT`
          - `FINANCED_BILLET`
          - `FINANCED_INSTALLMENT`
          - `GOOGLE_PAY`
          - `HOTCARD`
          - `HYBRID`
          - `MANUAL_TRANSFER`
          - `PAYPAL`
          - `PAYPAL_INTERNACIONAL`
          - `PICPAY`
          - `PIX`
          - `SAMSUNG_PAY`
          - `WALLET`"""
    endpoint = "/payments/api/v1/sales/history"
    params = {}
    if max_results is not None:
        params["max_results"] = max_results
    if page_token is not None:
        params["page_token"] = page_token
    if product_id is not None:
        params["product_id"] = product_id
    if start_date is not None:
        params["start_date"] = start_date
    if end_date is not None:
        params["end_date"] = end_date
    if sales_source is not None:
        params["sales_source"] = sales_source
    if transaction is not None:
        params["transaction"] = transaction
    if select is not None:
        params["select"] = select
    if buyer_name is not None:
        params["buyer_name"] = buyer_name
    if buyer_email is not None:
        params["buyer_email"] = buyer_email
    if offer_code is not None:
        params["offer_code"] = offer_code
    if commission_as is not None:
        params["commission_as"] = commission_as
    if transaction_status is not None:
        params["transaction_status"] = transaction_status
    if payment_type is not None:
        params["payment_type"] = payment_type
    result = await get_client().get(endpoint, params=params)
    return json.dumps(result, indent=2)


async def hotmart_sales_summary_list(
    transaction: Optional[str] = None,
    transaction_status: Optional[str] = None,
    max_results: Optional[int] = None,
    page_token: Optional[str] = None,
    product_id: Optional[int] = None,
    start_date: Optional[int] = None,
    end_date: Optional[int] = None,
    sales_source: Optional[str] = None,
    affiliate_name: Optional[str] = None,
    payment_type: Optional[str] = None,
    offer_code: Optional[str] = None,
    select: Optional[str] = None,
) -> str:
    """Sales Summary. Example: hotmart_sales_summary_list(transaction_status='APPROVED'). Don't use this for per-transaction details — use `hotmart_sales_history_list` for the raw list.
    
    Args:
        transaction: Transaction code
        transaction_status: Transaction status.
        Allowed values (case-sensitive, pass EXACTLY as listed):
          - `APPROVED`
          - `BLOCKED`
          - `CANCELLED`
          - `CHARGEBACK`
          - `COMPLETE`
          - `EXPIRED`
          - `NO_FUNDS`
          - `OVERDUE`
          - `PARTIALLY_REFUNDED`
          - `PRE_ORDER`
          - `PRINTED_BILLET`
          - `PROCESSING_TRANSACTION`
          - `PROTESTED`
          - `REFUNDED`
          - `STARTED`
          - `UNDER_ANALISYS`
          - `WAITING_PAYMENT`
        max_results: Max results per page
        page_token: Pagination token for the next page
        product_id: Product ID
        start_date: Start date. Unix timestamp in **milliseconds** (not seconds, not ISO). Ex: `1730419200000` = 2024-11-01 00:00 UTC. Python: `int(datetime(2024,11,1).timestamp() * 1000)`.
        end_date: End date. Unix timestamp in **milliseconds** (not seconds, not ISO). Ex: `1730419200000` = 2024-11-01 00:00 UTC. Python: `int(datetime(2024,11,1).timestamp() * 1000)`.
        sales_source: Sale source
        affiliate_name: Nome do afiliado
        payment_type: Payment type.
        Allowed values (case-sensitive, pass EXACTLY as listed):
          - `BILLET`
          - `CASH_PAYMENT`
          - `CREDIT_CARD`
          - `DIRECT_BANK_TRANSFER`
          - `DIRECT_DEBIT`
          - `FINANCED_BILLET`
          - `FINANCED_INSTALLMENT`
          - `GOOGLE_PAY`
          - `HOTCARD`
          - `HYBRID`
          - `MANUAL_TRANSFER`
          - `PAYPAL`
          - `PAYPAL_INTERNACIONAL`
          - `PICPAY`
          - `PIX`
          - `SAMSUNG_PAY`
          - `WALLET`
        offer_code: Offer code. Format: alphanumeric Hotmart code (ex: `H123A4B5`, not UUID, not int)
        select: Custom field selection in response"""
    endpoint = "/payments/api/v1/sales/summary"
    params = {}
    if transaction is not None:
        params["transaction"] = transaction
    if transaction_status is not None:
        params["transaction_status"] = transaction_status
    if max_results is not None:
        params["max_results"] = max_results
    if page_token is not None:
        params["page_token"] = page_token
    if product_id is not None:
        params["product_id"] = product_id
    if start_date is not None:
        params["start_date"] = start_date
    if end_date is not None:
        params["end_date"] = end_date
    if sales_source is not None:
        params["sales_source"] = sales_source
    if affiliate_name is not None:
        params["affiliate_name"] = affiliate_name
    if payment_type is not None:
        params["payment_type"] = payment_type
    if offer_code is not None:
        params["offer_code"] = offer_code
    if select is not None:
        params["select"] = select
    result = await get_client().get(endpoint, params=params)
    return json.dumps(result, indent=2)


async def hotmart_sales_participants_list(
    transaction: Optional[str] = None,
    transaction_status: Optional[str] = None,
    max_results: Optional[int] = None,
    page_token: Optional[str] = None,
    product_id: Optional[int] = None,
    start_date: Optional[int] = None,
    end_date: Optional[int] = None,
    buyer_email: Optional[str] = None,
    sales_source: Optional[str] = None,
    buyer_name: Optional[str] = None,
    affiliate_name: Optional[str] = None,
    commission_as: Optional[str] = None,
    select: Optional[str] = None,
) -> str:
    """Sales Participants. Example: hotmart_sales_participants_list(transaction_status='APPROVED').
    
    Args:
        transaction: Transaction code
        transaction_status: Transaction status.
        Allowed values (case-sensitive, pass EXACTLY as listed):
          - `APPROVED`
          - `BLOCKED`
          - `CANCELLED`
          - `CHARGEBACK`
          - `COMPLETE`
          - `EXPIRED`
          - `NO_FUNDS`
          - `OVERDUE`
          - `PARTIALLY_REFUNDED`
          - `PRE_ORDER`
          - `PRINTED_BILLET`
          - `PROCESSING_TRANSACTION`
          - `PROTESTED`
          - `REFUNDED`
          - `STARTED`
          - `UNDER_ANALISYS`
          - `WAITING_PAYMENT`
        max_results: Max results per page
        page_token: Pagination token for the next page
        product_id: Product ID
        start_date: Start date. Unix timestamp in **milliseconds** (not seconds, not ISO). Ex: `1730419200000` = 2024-11-01 00:00 UTC. Python: `int(datetime(2024,11,1).timestamp() * 1000)`.
        end_date: End date. Unix timestamp in **milliseconds** (not seconds, not ISO). Ex: `1730419200000` = 2024-11-01 00:00 UTC. Python: `int(datetime(2024,11,1).timestamp() * 1000)`.
        buyer_email: Buyer email
        sales_source: Sale source
        buyer_name: Buyer name
        affiliate_name: Nome do afiliado
        commission_as: Authenticated user's commission role. Allowed values: 'PRODUCER', 'COPRODUCER', 'AFFILIATE'
        select: Custom field selection in response"""
    endpoint = "/payments/api/v1/sales/users"
    params = {}
    if transaction is not None:
        params["transaction"] = transaction
    if transaction_status is not None:
        params["transaction_status"] = transaction_status
    if max_results is not None:
        params["max_results"] = max_results
    if page_token is not None:
        params["page_token"] = page_token
    if product_id is not None:
        params["product_id"] = product_id
    if start_date is not None:
        params["start_date"] = start_date
    if end_date is not None:
        params["end_date"] = end_date
    if buyer_email is not None:
        params["buyer_email"] = buyer_email
    if sales_source is not None:
        params["sales_source"] = sales_source
    if buyer_name is not None:
        params["buyer_name"] = buyer_name
    if affiliate_name is not None:
        params["affiliate_name"] = affiliate_name
    if commission_as is not None:
        params["commission_as"] = commission_as
    if select is not None:
        params["select"] = select
    result = await get_client().get(endpoint, params=params)
    return json.dumps(result, indent=2)


async def hotmart_sales_commissions_list(
    max_results: Optional[int] = None,
    page_token: Optional[str] = None,
    product_id: Optional[int] = None,
    start_date: Optional[int] = None,
    end_date: Optional[int] = None,
    transaction: Optional[str] = None,
    commission_as: Optional[str] = None,
    transaction_status: Optional[str] = None,
    select: Optional[str] = None,
) -> str:
    """Sales Commissions. Example: hotmart_sales_commissions_list(max_results=10).
    
    Args:
        max_results: Max results per page
        page_token: Pagination token for the next page
        product_id: Product ID
        start_date: Start date. Unix timestamp in **milliseconds** (not seconds, not ISO). Ex: `1730419200000` = 2024-11-01 00:00 UTC. Python: `int(datetime(2024,11,1).timestamp() * 1000)`.
        end_date: End date. Unix timestamp in **milliseconds** (not seconds, not ISO). Ex: `1730419200000` = 2024-11-01 00:00 UTC. Python: `int(datetime(2024,11,1).timestamp() * 1000)`.
        transaction: Transaction code
        commission_as: Authenticated user's commission role. Allowed values: 'PRODUCER', 'COPRODUCER', 'AFFILIATE'
        transaction_status: Transaction status.
        Allowed values (case-sensitive, pass EXACTLY as listed):
          - `APPROVED`
          - `BLOCKED`
          - `CANCELLED`
          - `CHARGEBACK`
          - `COMPLETE`
          - `EXPIRED`
          - `NO_FUNDS`
          - `OVERDUE`
          - `PARTIALLY_REFUNDED`
          - `PRE_ORDER`
          - `PRINTED_BILLET`
          - `PROCESSING_TRANSACTION`
          - `PROTESTED`
          - `REFUNDED`
          - `STARTED`
          - `UNDER_ANALISYS`
          - `WAITING_PAYMENT`
        select: Custom field selection in response"""
    endpoint = "/payments/api/v1/sales/commissions"
    params = {}
    if max_results is not None:
        params["max_results"] = max_results
    if page_token is not None:
        params["page_token"] = page_token
    if product_id is not None:
        params["product_id"] = product_id
    if start_date is not None:
        params["start_date"] = start_date
    if end_date is not None:
        params["end_date"] = end_date
    if transaction is not None:
        params["transaction"] = transaction
    if commission_as is not None:
        params["commission_as"] = commission_as
    if transaction_status is not None:
        params["transaction_status"] = transaction_status
    if select is not None:
        params["select"] = select
    result = await get_client().get(endpoint, params=params)
    return json.dumps(result, indent=2)


async def hotmart_sales_price_details_list(
    transaction: Optional[str] = None,
    transaction_status: Optional[str] = None,
    max_results: Optional[int] = None,
    page_token: Optional[str] = None,
    product_id: Optional[int] = None,
    start_date: Optional[int] = None,
    end_date: Optional[int] = None,
    payment_type: Optional[str] = None,
    select: Optional[str] = None,
) -> str:
    """Sales Price Details. Example: hotmart_sales_price_details_list(transaction_status='APPROVED').
    
    Args:
        transaction: Transaction code
        transaction_status: Transaction status.
        Allowed values (case-sensitive, pass EXACTLY as listed):
          - `APPROVED`
          - `BLOCKED`
          - `CANCELLED`
          - `CHARGEBACK`
          - `COMPLETE`
          - `EXPIRED`
          - `NO_FUNDS`
          - `OVERDUE`
          - `PARTIALLY_REFUNDED`
          - `PRE_ORDER`
          - `PRINTED_BILLET`
          - `PROCESSING_TRANSACTION`
          - `PROTESTED`
          - `REFUNDED`
          - `STARTED`
          - `UNDER_ANALISYS`
          - `WAITING_PAYMENT`
        max_results: Max results per page
        page_token: Pagination token for the next page
        product_id: Product ID
        start_date: Start date. Unix timestamp in **milliseconds** (not seconds, not ISO). Ex: `1730419200000` = 2024-11-01 00:00 UTC. Python: `int(datetime(2024,11,1).timestamp() * 1000)`.
        end_date: End date. Unix timestamp in **milliseconds** (not seconds, not ISO). Ex: `1730419200000` = 2024-11-01 00:00 UTC. Python: `int(datetime(2024,11,1).timestamp() * 1000)`.
        payment_type: Payment type.
        Allowed values (case-sensitive, pass EXACTLY as listed):
          - `BILLET`
          - `CASH_PAYMENT`
          - `CREDIT_CARD`
          - `DIRECT_BANK_TRANSFER`
          - `DIRECT_DEBIT`
          - `FINANCED_BILLET`
          - `FINANCED_INSTALLMENT`
          - `GOOGLE_PAY`
          - `HOTCARD`
          - `HYBRID`
          - `MANUAL_TRANSFER`
          - `PAYPAL`
          - `PAYPAL_INTERNACIONAL`
          - `PICPAY`
          - `PIX`
          - `SAMSUNG_PAY`
          - `WALLET`
        select: Custom field selection in response"""
    endpoint = "/payments/api/v1/sales/price/details"
    params = {}
    if transaction is not None:
        params["transaction"] = transaction
    if transaction_status is not None:
        params["transaction_status"] = transaction_status
    if max_results is not None:
        params["max_results"] = max_results
    if page_token is not None:
        params["page_token"] = page_token
    if product_id is not None:
        params["product_id"] = product_id
    if start_date is not None:
        params["start_date"] = start_date
    if end_date is not None:
        params["end_date"] = end_date
    if payment_type is not None:
        params["payment_type"] = payment_type
    if select is not None:
        params["select"] = select
    result = await get_client().get(endpoint, params=params)
    return json.dumps(result, indent=2)


async def hotmart_sale_refund(
    transaction_code: str,
) -> str:
    """Sales Refund. Example: hotmart_sale_refund(transaction_code='ABC123XY').
    
    Args:
        transaction_code: Transaction code. Format: alphanumeric Hotmart code (ex: `H123A4B5`, not UUID, not int)"""
    endpoint = f"/payments/api/v1/sales/{transaction_code}/refund"
    result = await get_client().put(endpoint)
    return json.dumps(result, indent=2)
