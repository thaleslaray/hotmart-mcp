"""Auto-generated Hotmart API tools — subscriptions."""

import json
from typing import Optional

from hotmart_mcp._shared import get_client

__all__ = ["get_subscriptions", "get_subscriptions_summary", "get_subscription_transactions", "get_subscriber_purchases", "cancel_subscription", "batch_cancel_subscriptions", "reactivate_subscription", "batch_reactivate_subscriptions", "change_subscription_due_day"]


async def get_subscriptions(
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
    """Get Subscriptions
    
    Retorna a lista de assinaturas.
    
    Args:
        max_results: Número máximo de resultados por página
        page_token: Token de paginação para a próxima página
        product_id: ID do produto
        plan: Nomes dos planos
        plan_id: ID do plano
        accession_date: Data de adesão inicial (timestamp em milissegundos)
        end_accession_date: Data de adesão final (timestamp em milissegundos)
        status: Status da assinatura. Values: ACTIVE, INACTIVE, DELAYED, CANCELLED_BY_CUSTOMER, CANCELLED_BY_SELLER, CANCELLED_BY_ADMIN, STARTED, OVERDUE
        subscriber_code: Código do assinante
        subscriber_email: E-mail do assinante
        transaction: Código da transação
        trial: Filtrar por trial
        cancelation_date: Data de cancelamento inicial (timestamp em milissegundos)
        end_cancelation_date: Data de cancelamento final (timestamp em milissegundos)
        date_next_charge: Data da próxima cobrança inicial (timestamp em milissegundos)
        end_date_next_charge: Data da próxima cobrança final (timestamp em milissegundos)
        select: Seleção de campos customizados na resposta"""
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


async def get_subscriptions_summary(
    max_results: Optional[int] = None,
    page_token: Optional[str] = None,
    product_id: Optional[int] = None,
    subscriber_code: Optional[int] = None,
    accession_date: Optional[int] = None,
    end_accession_date: Optional[int] = None,
    date_next_charge: Optional[int] = None,
    select: Optional[str] = None,
) -> str:
    """Subscription Summary
    
    Retorna o resumo das assinaturas.
    
    Args:
        max_results: Número máximo de resultados por página
        page_token: Token de paginação para a próxima página
        product_id: ID do produto
        subscriber_code: Código do assinante
        accession_date: Data de adesão inicial (timestamp em milissegundos)
        end_accession_date: Data de adesão final (timestamp em milissegundos)
        date_next_charge: Data da próxima cobrança (timestamp em milissegundos)
        select: Seleção de campos customizados na resposta"""
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


async def get_subscription_transactions(
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
    """Subscription Transactions
    
    Retorna as transações de assinatura. Dados com atraso de 24h. Por padrão retorna os últimos 30 dias.
    
    Args:
        max_results: Número máximo de resultados por página
        page_token: Token de paginação para a próxima página
        product_id: ID do produto
        transaction: Código da transação
        subscriber_name: Nome do assinante
        subscriber_email: E-mail do assinante
        billing_type: Tipo de cobrança. Values: SUBSCRIPTION, SMART_INSTALLMENT, SMART_RECOVERY
        subscription_status: Status da assinatura. Values: STARTED, INACTIVE, ACTIVE, DELAYED, CANCELLED, CANCELLED_BY_ADMIN, CANCELLED_BY_CUSTOMER, CANCELLED_BY_SELLER, OVERDUE
        recurrency_status: Status da recorrência. Values: PAID, NOT_PAID, CLAIMED, REFUNDED, CHARGEBACK
        purchase_status: Status da compra
        transaction_date: Data da transação inicial (timestamp em milissegundos)
        end_transaction_date: Data da transação final (timestamp em milissegundos)
        offer_code: Código da oferta
        purchase_payment_type: Tipo de pagamento da compra. Values: BILLET, CASH_PAYMENT, CREDIT_CARD, DIRECT_BANK_TRANSFER, DIRECT_DEBIT, FINANCED_BILLET, FINANCED_INSTALLMENT, GOOGLE_PAY, HOTCARD, HYBRID, MANUAL_TRANSFER, PAYPAL, PAYPAL_INTERNACIONAL, PICPAY, PIX, SAMSUNG_PAY, WALLET
        subscriber_code: Código do assinante
        select: Seleção de campos customizados na resposta"""
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


async def get_subscriber_purchases(
    subscriber_code: str,
) -> str:
    """Subscriber Purchases
    
    Retorna as compras de um assinante.
    
    Args:
        subscriber_code: Código do assinante"""
    endpoint = f"/payments/api/v1/subscriptions/{subscriber_code}/purchases"
    result = await get_client().get(endpoint)
    return json.dumps(result, indent=2)


async def cancel_subscription(
    subscriber_code: str,
    send_mail: Optional[bool] = None,
) -> str:
    """Cancel Subscription
    
    Cancela uma assinatura.
    
    Args:
        subscriber_code: Código do assinante
        send_mail: Enviar e-mail de notificação ao assinante"""
    endpoint = f"/payments/api/v1/subscriptions/{subscriber_code}/cancel"
    body = {}
    if send_mail is not None:
        body["send_mail"] = send_mail
    result = await get_client().post(endpoint, json=body)
    return json.dumps(result, indent=2)


async def batch_cancel_subscriptions(
    subscriber_code: list[str],
    send_mail: Optional[bool] = None,
) -> str:
    """Batch Cancel Subscriptions
    
    Cancela múltiplas assinaturas em lote.
    
    Args:
        subscriber_code: Lista de códigos de assinantes
        send_mail: Enviar e-mail de notificação aos assinantes"""
    endpoint = "/payments/api/v1/subscriptions/cancel"
    body = {}
    body["subscriber_code"] = subscriber_code
    if send_mail is not None:
        body["send_mail"] = send_mail
    result = await get_client().post(endpoint, json=body)
    return json.dumps(result, indent=2)


async def reactivate_subscription(
    subscriber_code: str,
    charge: Optional[bool] = None,
) -> str:
    """Reactivate Subscription
    
    Reativa uma assinatura. O assinante deve aceitar via link por e-mail (validade de 3 dias).
    
    Args:
        subscriber_code: Código do assinante
        charge: Cobrar imediatamente"""
    endpoint = f"/payments/api/v1/subscriptions/{subscriber_code}/reactivate"
    body = {}
    if charge is not None:
        body["charge"] = charge
    result = await get_client().post(endpoint, json=body)
    return json.dumps(result, indent=2)


async def batch_reactivate_subscriptions(
    subscriber_code: list[str],
    charge: Optional[bool] = None,
) -> str:
    """Batch Reactivate Subscriptions
    
    Reativa múltiplas assinaturas em lote.
    
    Args:
        subscriber_code: Lista de códigos de assinantes
        charge: Cobrar imediatamente"""
    endpoint = "/payments/api/v1/subscriptions/reactivate"
    body = {}
    body["subscriber_code"] = subscriber_code
    if charge is not None:
        body["charge"] = charge
    result = await get_client().post(endpoint, json=body)
    return json.dumps(result, indent=2)


async def change_subscription_due_day(
    subscriber_code: str,
    due_day: int,
) -> str:
    """Change Due Day
    
    Altera o dia de vencimento de uma assinatura. Somente para assinaturas ACTIVE ou DELAYED. Não disponível para trial. O dia 31 será ajustado para 30 em meses mais curtos.
    
    Args:
        subscriber_code: Código do assinante
        due_day: Novo dia de vencimento (1-31)"""
    endpoint = f"/payments/api/v1/subscriptions/{subscriber_code}"
    body = {}
    body["due_day"] = due_day
    result = await get_client().patch(endpoint, json=body)
    return json.dumps(result, indent=2)
