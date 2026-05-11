"""Auto-generated Hotmart API tools — subscriptions."""

import json
from typing import Optional

from hotmart_mcp._shared import get_client

__all__ = ["hotmart_subscriptions_list", "hotmart_subscriptions_summary_list", "hotmart_subscription_transactions_list", "hotmart_subscriber_purchases_list", "hotmart_subscription_cancel", "hotmart_batch_subscriptions_cancel", "hotmart_subscription_reactivate", "hotmart_batch_subscriptions_reactivate", "hotmart_subscription_due_day_update"]


async def hotmart_subscriptions_list(
    max_results: Optional[int] = None,
    page_token: Optional[str] = None,
    product_id: Optional[int] = None,
    plan: Optional[list[str]] = None,
    plan_id: Optional[int] = None,
    accession_date: Optional[int] = None,
    end_accession_date: Optional[int] = None,
    status: Optional[str] = None,
    subscriber_code: Optional[str] = None,
    subscriber_email: Optional[str] = None,
    transaction: Optional[str] = None,
    trial: Optional[bool] = None,
    cancelation_date: Optional[int] = None,
    end_cancelation_date: Optional[int] = None,
    date_next_charge: Optional[int] = None,
    end_date_next_charge: Optional[int] = None,
    select: Optional[str] = None,
) -> str:
    """Get Subscriptions. Example: hotmart_subscriptions_list(max_results=10). Don't use this for payment events — use `hotmart_subscription_transactions_list` for charges/refunds per subscription.
    
    Args:
        max_results: Max results per page
        page_token: Pagination token for the next page
        product_id: Product ID
        plan: Nomes dos planos. Pass a JSON array of strings, e.g. `['ABC123XY', 'DEF456ZW']`.
        plan_id: ID do plano
        accession_date: Subscription start date (lower bound). Unix timestamp in **milliseconds** (not seconds, not ISO). Ex: `1730419200000` = 2024-11-01 00:00 UTC. Python: `int(datetime(2024,11,1).timestamp() * 1000)`.
        end_accession_date: Subscription start date (upper bound). Unix timestamp in **milliseconds** (not seconds, not ISO). Ex: `1730419200000` = 2024-11-01 00:00 UTC. Python: `int(datetime(2024,11,1).timestamp() * 1000)`.
        status: Subscription status.
        Allowed values (case-sensitive, pass EXACTLY as listed):
          - `ACTIVE`
          - `INACTIVE`
          - `DELAYED`
          - `CANCELLED_BY_CUSTOMER`
          - `CANCELLED_BY_SELLER`
          - `CANCELLED_BY_ADMIN`
          - `STARTED`
          - `OVERDUE`
        subscriber_code: Subscriber code. Format: alphanumeric Hotmart code (ex: `H123A4B5`, not UUID, not int)
        subscriber_email: Email do assinante
        transaction: Transaction code
        trial: Filtrar por trial
        cancelation_date: Data de cancelamento inicial. Unix timestamp in **milliseconds** (not seconds, not ISO). Ex: `1730419200000` = 2024-11-01 00:00 UTC. Python: `int(datetime(2024,11,1).timestamp() * 1000)`.
        end_cancelation_date: Data de cancelamento final. Unix timestamp in **milliseconds** (not seconds, not ISO). Ex: `1730419200000` = 2024-11-01 00:00 UTC. Python: `int(datetime(2024,11,1).timestamp() * 1000)`.
        date_next_charge: Data da próxima cobrança inicial. Unix timestamp in **milliseconds** (not seconds, not ISO). Ex: `1730419200000` = 2024-11-01 00:00 UTC. Python: `int(datetime(2024,11,1).timestamp() * 1000)`.
        end_date_next_charge: Data da próxima cobrança final. Unix timestamp in **milliseconds** (not seconds, not ISO). Ex: `1730419200000` = 2024-11-01 00:00 UTC. Python: `int(datetime(2024,11,1).timestamp() * 1000)`.
        select: Custom field selection in response"""
    endpoint = "/payments/api/v1/subscriptions"
    params = {}
    if max_results is not None:
        params["max_results"] = max_results
    if page_token is not None:
        params["page_token"] = page_token
    if product_id is not None:
        params["product_id"] = product_id
    if plan is not None:
        params["plan"] = plan
    if plan_id is not None:
        params["plan_id"] = plan_id
    if accession_date is not None:
        params["accession_date"] = accession_date
    if end_accession_date is not None:
        params["end_accession_date"] = end_accession_date
    if status is not None:
        params["status"] = status
    if subscriber_code is not None:
        params["subscriber_code"] = subscriber_code
    if subscriber_email is not None:
        params["subscriber_email"] = subscriber_email
    if transaction is not None:
        params["transaction"] = transaction
    if trial is not None:
        params["trial"] = trial
    if cancelation_date is not None:
        params["cancelation_date"] = cancelation_date
    if end_cancelation_date is not None:
        params["end_cancelation_date"] = end_cancelation_date
    if date_next_charge is not None:
        params["date_next_charge"] = date_next_charge
    if end_date_next_charge is not None:
        params["end_date_next_charge"] = end_date_next_charge
    if select is not None:
        params["select"] = select
    result = await get_client().get(endpoint, params=params)
    return json.dumps(result, indent=2)


async def hotmart_subscriptions_summary_list(
    max_results: Optional[int] = None,
    page_token: Optional[str] = None,
    product_id: Optional[int] = None,
    subscriber_code: Optional[int] = None,
    accession_date: Optional[int] = None,
    end_accession_date: Optional[int] = None,
    date_next_charge: Optional[int] = None,
    select: Optional[str] = None,
) -> str:
    """Subscription Summary. Example: hotmart_subscriptions_summary_list(max_results=10).
    
    Args:
        max_results: Max results per page
        page_token: Pagination token for the next page
        product_id: Product ID
        subscriber_code: Subscriber code
        accession_date: Subscription start date (lower bound). Unix timestamp in **milliseconds** (not seconds, not ISO). Ex: `1730419200000` = 2024-11-01 00:00 UTC. Python: `int(datetime(2024,11,1).timestamp() * 1000)`.
        end_accession_date: Subscription start date (upper bound). Unix timestamp in **milliseconds** (not seconds, not ISO). Ex: `1730419200000` = 2024-11-01 00:00 UTC. Python: `int(datetime(2024,11,1).timestamp() * 1000)`.
        date_next_charge: Data da próxima cobrança. Unix timestamp in **milliseconds** (not seconds, not ISO). Ex: `1730419200000` = 2024-11-01 00:00 UTC. Python: `int(datetime(2024,11,1).timestamp() * 1000)`.
        select: Custom field selection in response"""
    endpoint = "/payments/api/v1/subscriptions/summary"
    params = {}
    if max_results is not None:
        params["max_results"] = max_results
    if page_token is not None:
        params["page_token"] = page_token
    if product_id is not None:
        params["product_id"] = product_id
    if subscriber_code is not None:
        params["subscriber_code"] = subscriber_code
    if accession_date is not None:
        params["accession_date"] = accession_date
    if end_accession_date is not None:
        params["end_accession_date"] = end_accession_date
    if date_next_charge is not None:
        params["date_next_charge"] = date_next_charge
    if select is not None:
        params["select"] = select
    result = await get_client().get(endpoint, params=params)
    return json.dumps(result, indent=2)


async def hotmart_subscription_transactions_list(
    max_results: Optional[int] = None,
    page_token: Optional[str] = None,
    product_id: Optional[int] = None,
    transaction: Optional[str] = None,
    subscriber_name: Optional[str] = None,
    subscriber_email: Optional[str] = None,
    billing_type: Optional[str] = None,
    subscription_status: Optional[str] = None,
    recurrency_status: Optional[str] = None,
    purchase_status: Optional[str] = None,
    transaction_date: Optional[int] = None,
    end_transaction_date: Optional[int] = None,
    offer_code: Optional[str] = None,
    purchase_payment_type: Optional[str] = None,
    subscriber_code: Optional[str] = None,
    select: Optional[str] = None,
) -> str:
    """Subscription Transactions. Example: hotmart_subscription_transactions_list(max_results=10). Don't use this for the subscription list itself — use `hotmart_subscriptions_list`.
    
    Args:
        max_results: Max results per page
        page_token: Pagination token for the next page
        product_id: Product ID
        transaction: Transaction code
        subscriber_name: Nome do assinante
        subscriber_email: Email do assinante
        billing_type: Tipo de cobrança. Allowed values: 'SUBSCRIPTION', 'SMART_INSTALLMENT', 'SMART_RECOVERY'
        subscription_status: Subscription status.
        Allowed values (case-sensitive, pass EXACTLY as listed):
          - `STARTED`
          - `INACTIVE`
          - `ACTIVE`
          - `DELAYED`
          - `CANCELLED`
          - `CANCELLED_BY_ADMIN`
          - `CANCELLED_BY_CUSTOMER`
          - `CANCELLED_BY_SELLER`
          - `OVERDUE`
        recurrency_status: Status da recorrência.
        Allowed values (case-sensitive, pass EXACTLY as listed):
          - `PAID`
          - `NOT_PAID`
          - `CLAIMED`
          - `REFUNDED`
          - `CHARGEBACK`
        purchase_status: Status da compra
        transaction_date: Data da transação inicial. Unix timestamp in **milliseconds** (not seconds, not ISO). Ex: `1730419200000` = 2024-11-01 00:00 UTC. Python: `int(datetime(2024,11,1).timestamp() * 1000)`.
        end_transaction_date: Data da transação final. Unix timestamp in **milliseconds** (not seconds, not ISO). Ex: `1730419200000` = 2024-11-01 00:00 UTC. Python: `int(datetime(2024,11,1).timestamp() * 1000)`.
        offer_code: Offer code. Format: alphanumeric Hotmart code (ex: `H123A4B5`, not UUID, not int)
        purchase_payment_type: Payment type da compra.
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
        Note: API uses English `'BILLET'` (NOT Portuguese `'BOLETO'`).
        subscriber_code: Subscriber code. Format: alphanumeric Hotmart code (ex: `H123A4B5`, not UUID, not int)
        select: Custom field selection in response"""
    endpoint = "/payments/api/v1/subscriptions/transactions"
    params = {}
    if max_results is not None:
        params["max_results"] = max_results
    if page_token is not None:
        params["page_token"] = page_token
    if product_id is not None:
        params["product_id"] = product_id
    if transaction is not None:
        params["transaction"] = transaction
    if subscriber_name is not None:
        params["subscriber_name"] = subscriber_name
    if subscriber_email is not None:
        params["subscriber_email"] = subscriber_email
    if billing_type is not None:
        params["billing_type"] = billing_type
    if subscription_status is not None:
        params["subscription_status"] = subscription_status
    if recurrency_status is not None:
        params["recurrency_status"] = recurrency_status
    if purchase_status is not None:
        params["purchase_status"] = purchase_status
    if transaction_date is not None:
        params["transaction_date"] = transaction_date
    if end_transaction_date is not None:
        params["end_transaction_date"] = end_transaction_date
    if offer_code is not None:
        params["offer_code"] = offer_code
    if purchase_payment_type is not None:
        params["purchase_payment_type"] = purchase_payment_type
    if subscriber_code is not None:
        params["subscriber_code"] = subscriber_code
    if select is not None:
        params["select"] = select
    result = await get_client().get(endpoint, params=params)
    return json.dumps(result, indent=2)


async def hotmart_subscriber_purchases_list(
    subscriber_code: str,
) -> str:
    """Subscriber Purchases. Example: hotmart_subscriber_purchases_list(subscriber_code='ABC123XY').
    
    Args:
        subscriber_code: Subscriber code. Format: alphanumeric Hotmart code (ex: `H123A4B5`, not UUID, not int)"""
    endpoint = f"/payments/api/v1/subscriptions/{subscriber_code}/purchases"
    result = await get_client().get(endpoint)
    return json.dumps(result, indent=2)


async def hotmart_subscription_cancel(
    subscriber_code: str,
    send_mail: Optional[bool] = None,
) -> str:
    """Cancel Subscription. Example: hotmart_subscription_cancel(subscriber_code='ABC123XY'). Use this for ONE subscriber_code. For 2+ subscriptions, use `hotmart_batch_subscriptions_cancel`.
    
    Args:
        subscriber_code: Subscriber code. Format: alphanumeric Hotmart code (ex: `H123A4B5`, not UUID, not int)
        send_mail: Enviar e-mail de notificação ao assinante"""
    endpoint = f"/payments/api/v1/subscriptions/{subscriber_code}/cancel"
    body = {}
    if send_mail is not None:
        body["send_mail"] = send_mail
    result = await get_client().post(endpoint, json=body)
    return json.dumps(result, indent=2)


async def hotmart_batch_subscriptions_cancel(
    subscriber_code: list[str],
    send_mail: Optional[bool] = None,
) -> str:
    """Batch Cancel Subscriptions. Use this for multiple subscriber_codes at once. For a single one, prefer `hotmart_subscription_cancel`.
    
    Args:
        subscriber_code: List of subscriber codess. Pass a JSON array of strings, e.g. `['ABC123XY', 'DEF456ZW']`.
        send_mail: Enviar e-mail de notificação aos assinantes"""
    endpoint = "/payments/api/v1/subscriptions/cancel"
    body = {}
    body["subscriber_code"] = subscriber_code
    if send_mail is not None:
        body["send_mail"] = send_mail
    result = await get_client().post(endpoint, json=body)
    return json.dumps(result, indent=2)


async def hotmart_subscription_reactivate(
    subscriber_code: str,
    charge: Optional[bool] = None,
) -> str:
    """Reactivate Subscription. Example: hotmart_subscription_reactivate(subscriber_code='ABC123XY'). Use this for ONE subscriber_code. For 2+, use `hotmart_batch_subscriptions_reactivate`.
    
    Args:
        subscriber_code: Subscriber code. Format: alphanumeric Hotmart code (ex: `H123A4B5`, not UUID, not int)
        charge: Cobrar imediatamente"""
    endpoint = f"/payments/api/v1/subscriptions/{subscriber_code}/reactivate"
    body = {}
    if charge is not None:
        body["charge"] = charge
    result = await get_client().post(endpoint, json=body)
    return json.dumps(result, indent=2)


async def hotmart_batch_subscriptions_reactivate(
    subscriber_code: list[str],
    charge: Optional[bool] = None,
) -> str:
    """Batch Reactivate Subscriptions. Use this for multiple subscriber_codes at once. For a single one, prefer `hotmart_subscription_reactivate`.
    
    Args:
        subscriber_code: List of subscriber codess. Pass a JSON array of strings, e.g. `['ABC123XY', 'DEF456ZW']`.
        charge: Cobrar imediatamente"""
    endpoint = "/payments/api/v1/subscriptions/reactivate"
    body = {}
    body["subscriber_code"] = subscriber_code
    if charge is not None:
        body["charge"] = charge
    result = await get_client().post(endpoint, json=body)
    return json.dumps(result, indent=2)


async def hotmart_subscription_due_day_update(
    subscriber_code: str,
    due_day: int,
) -> str:
    """Change Due Day. Example: hotmart_subscription_due_day_update(subscriber_code='ABC123XY').
    
    Args:
        subscriber_code: Subscriber code. Format: alphanumeric Hotmart code (ex: `H123A4B5`, not UUID, not int)
        due_day: Novo dia de vencimento (1-31)"""
    endpoint = f"/payments/api/v1/subscriptions/{subscriber_code}"
    body = {}
    body["due_day"] = due_day
    result = await get_client().patch(endpoint, json=body)
    return json.dumps(result, indent=2)
