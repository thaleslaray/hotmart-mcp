"""Auto-generated Hotmart API tools — sales."""

import json
from typing import Optional

from hotmart_mcp._shared import get_client

__all__ = ["get_sales_history", "get_sales_summary", "get_sales_participants", "get_sales_commissions", "get_sales_price_details", "refund_sale"]


async def get_sales_history(
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
    """Sales History
    
    Retorna o histórico de vendas. Sem os filtros transaction ou transaction_status, apenas vendas com status APPROVED e COMPLETE são retornadas.
    
    Args:
        max_results: Número máximo de resultados por página
        page_token: Token de paginação para a próxima página
        product_id: ID do produto
        start_date: Data inicial (timestamp em milissegundos desde epoch). Timestamp em **milissegundos** desde epoch (não segundos, não ISO). Ex: `1730419200000` = 2024-11-01 00:00 UTC. Em Python: `int(datetime(2024,11,1).timestamp() * 1000)`.
        end_date: Data final (timestamp em milissegundos desde epoch). Timestamp em **milissegundos** desde epoch (não segundos, não ISO). Ex: `1730419200000` = 2024-11-01 00:00 UTC. Em Python: `int(datetime(2024,11,1).timestamp() * 1000)`.
        sales_source: Origem da venda
        transaction: Código da transação
        select: Seleção de campos customizados na resposta
        buyer_name: Nome do comprador
        buyer_email: E-mail do comprador
        offer_code: Código da oferta. Formato: código alfanumérico Hotmart (ex: `H123A4B5`, não é UUID nem int)
        commission_as: Papel de comissão do usuário autenticado. Valores aceitos: 'PRODUCER', 'COPRODUCER', 'AFFILIATE'
        transaction_status: Status da transação.
        Valores aceitos (case-sensitive, passe EXATAMENTE como abaixo):
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
        payment_type: Tipo de pagamento.
        Valores aceitos (case-sensitive, passe EXATAMENTE como abaixo):
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


async def get_sales_summary(
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
    """Sales Summary
    
    Retorna o resumo das vendas.
    
    Args:
        transaction: Código da transação
        transaction_status: Status da transação.
        Valores aceitos (case-sensitive, passe EXATAMENTE como abaixo):
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
        max_results: Número máximo de resultados por página
        page_token: Token de paginação para a próxima página
        product_id: ID do produto
        start_date: Data inicial (timestamp em milissegundos desde epoch). Timestamp em **milissegundos** desde epoch (não segundos, não ISO). Ex: `1730419200000` = 2024-11-01 00:00 UTC. Em Python: `int(datetime(2024,11,1).timestamp() * 1000)`.
        end_date: Data final (timestamp em milissegundos desde epoch). Timestamp em **milissegundos** desde epoch (não segundos, não ISO). Ex: `1730419200000` = 2024-11-01 00:00 UTC. Em Python: `int(datetime(2024,11,1).timestamp() * 1000)`.
        sales_source: Origem da venda
        affiliate_name: Nome do afiliado
        payment_type: Tipo de pagamento.
        Valores aceitos (case-sensitive, passe EXATAMENTE como abaixo):
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
        offer_code: Código da oferta. Formato: código alfanumérico Hotmart (ex: `H123A4B5`, não é UUID nem int)
        select: Seleção de campos customizados na resposta"""
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


async def get_sales_participants(
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
    """Sales Participants
    
    Retorna os participantes de uma venda (produtor, afiliado, coprodutor).
    
    Args:
        transaction: Código da transação
        transaction_status: Status da transação.
        Valores aceitos (case-sensitive, passe EXATAMENTE como abaixo):
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
        max_results: Número máximo de resultados por página
        page_token: Token de paginação para a próxima página
        product_id: ID do produto
        start_date: Data inicial (timestamp em milissegundos desde epoch). Timestamp em **milissegundos** desde epoch (não segundos, não ISO). Ex: `1730419200000` = 2024-11-01 00:00 UTC. Em Python: `int(datetime(2024,11,1).timestamp() * 1000)`.
        end_date: Data final (timestamp em milissegundos desde epoch). Timestamp em **milissegundos** desde epoch (não segundos, não ISO). Ex: `1730419200000` = 2024-11-01 00:00 UTC. Em Python: `int(datetime(2024,11,1).timestamp() * 1000)`.
        buyer_email: E-mail do comprador
        sales_source: Origem da venda
        buyer_name: Nome do comprador
        affiliate_name: Nome do afiliado
        commission_as: Papel de comissão do usuário autenticado. Valores aceitos: 'PRODUCER', 'COPRODUCER', 'AFFILIATE'
        select: Seleção de campos customizados na resposta"""
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


async def get_sales_commissions(
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
    """Sales Commissions
    
    Retorna as comissões de vendas.
    
    Args:
        max_results: Número máximo de resultados por página
        page_token: Token de paginação para a próxima página
        product_id: ID do produto
        start_date: Data inicial (timestamp em milissegundos desde epoch). Timestamp em **milissegundos** desde epoch (não segundos, não ISO). Ex: `1730419200000` = 2024-11-01 00:00 UTC. Em Python: `int(datetime(2024,11,1).timestamp() * 1000)`.
        end_date: Data final (timestamp em milissegundos desde epoch). Timestamp em **milissegundos** desde epoch (não segundos, não ISO). Ex: `1730419200000` = 2024-11-01 00:00 UTC. Em Python: `int(datetime(2024,11,1).timestamp() * 1000)`.
        transaction: Código da transação
        commission_as: Papel de comissão do usuário autenticado. Valores aceitos: 'PRODUCER', 'COPRODUCER', 'AFFILIATE'
        transaction_status: Status da transação.
        Valores aceitos (case-sensitive, passe EXATAMENTE como abaixo):
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
        select: Seleção de campos customizados na resposta"""
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


async def get_sales_price_details(
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
    """Sales Price Details
    
    Retorna os detalhes de preço das vendas. Sem os filtros transaction ou transaction_status, apenas vendas com status APPROVED e COMPLETE são retornadas.
    
    Args:
        transaction: Código da transação
        transaction_status: Status da transação.
        Valores aceitos (case-sensitive, passe EXATAMENTE como abaixo):
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
        max_results: Número máximo de resultados por página
        page_token: Token de paginação para a próxima página
        product_id: ID do produto
        start_date: Data inicial (timestamp em milissegundos desde epoch). Timestamp em **milissegundos** desde epoch (não segundos, não ISO). Ex: `1730419200000` = 2024-11-01 00:00 UTC. Em Python: `int(datetime(2024,11,1).timestamp() * 1000)`.
        end_date: Data final (timestamp em milissegundos desde epoch). Timestamp em **milissegundos** desde epoch (não segundos, não ISO). Ex: `1730419200000` = 2024-11-01 00:00 UTC. Em Python: `int(datetime(2024,11,1).timestamp() * 1000)`.
        payment_type: Tipo de pagamento.
        Valores aceitos (case-sensitive, passe EXATAMENTE como abaixo):
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
        select: Seleção de campos customizados na resposta"""
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


async def refund_sale(
    transaction_code: str,
) -> str:
    """Sales Refund
    
    Realiza o reembolso de uma venda. A venda deve estar com status APPROVED ou COMPLETE. Não disponível para trial, BACS ou SEPA. Janela de reembolso de 7 a 30 dias (máximo 60).
    
    Args:
        transaction_code: Código da transação. Formato: código alfanumérico Hotmart (ex: `H123A4B5`, não é UUID nem int)"""
    endpoint = f"/payments/api/v1/sales/{transaction_code}/refund"
    result = await get_client().put(endpoint)
    return json.dumps(result, indent=2)
