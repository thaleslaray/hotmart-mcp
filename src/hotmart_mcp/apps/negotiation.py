"""Negotiation form — interactive Prefab UI app pra parcelamento."""
from __future__ import annotations

from typing import Optional

from prefab_ui import PrefabApp
from prefab_ui.components import (
    Alert, AlertDescription, AlertTitle, Card, CardContent, CardHeader,
    CardTitle, Column, Grid, Heading, Metric, Text,
)

from hotmart_mcp._shared import get_client


async def hotmart_negotiation_preview_app(
    subscription_id: str,
    payment_type: str = "BILLET",
    recurrences: int = 1,
    discount: Optional[float] = None,
) -> PrefabApp:
    """Preview de proposta de negociação antes de gerar.

    Mostra os parâmetros e dispara o `hotmart_negotiation_generate` se
    confirmado. Use pra 'simular negociação pro assinante X', 'preview
    parcelamento'. NÃO gera por padrão — só prévia visual.

    Args:
        subscription_id: ID/code da assinatura inadimplente.
        payment_type: BILLET | PIX | CREDIT_CARD. **Note: API uses English 'BILLET' (NOT 'BOLETO')**.
        recurrences: Número de parcelas (1 = à vista).
        discount: Desconto como **fração 0-1** (ex: 0.25 = 25% off). NOT percent.
    """
    discount_pct = (discount * 100) if discount else 0

    with PrefabApp() as app:
        with Column(gap=4, css_class="p-6"):
            Heading(content="Preview de Negociação")

            with Alert():
                AlertTitle(content="Apenas prévia — não foi gerado ainda")
                AlertDescription(
                    content=(
                        "Esta tela mostra o que será gerado se você confirmar. "
                        "Pra emitir de fato, peça ao Claude: "
                        f"'gera negociação pra {subscription_id} agora'."
                    ),
                )

            with Card():
                with CardHeader():
                    CardTitle(content="Parâmetros")
                with CardContent():
                    with Grid(columns=[1, 1], gap=4):
                        with Card():
                            with CardHeader():
                                CardTitle(content="Assinatura")
                            with CardContent():
                                Metric(label="Code", value=subscription_id)
                        with Card():
                            with CardHeader():
                                CardTitle(content="Pagamento")
                            with CardContent():
                                Metric(label="Método", value=payment_type)
                        with Card():
                            with CardHeader():
                                CardTitle(content="Parcelas")
                            with CardContent():
                                Metric(
                                    label="Recorrências",
                                    value=f"{recurrences}x" if recurrences > 1 else "À vista",
                                )
                        with Card():
                            with CardHeader():
                                CardTitle(content="Desconto")
                            with CardContent():
                                Metric(
                                    label="Off",
                                    value=f"{discount_pct:.0f}%" if discount else "—",
                                )

            with Card():
                with CardHeader():
                    CardTitle(content="Caveats importantes")
                with CardContent():
                    Text(
                        content=(
                            "• Cuidado com discount > 0.5 — Hotmart pode bloquear. "
                            "• BILLET (não BOLETO) é o enum correto. "
                            "• Negociação não pode ser desfeita após confirmar."
                        ),
                    )
    return app


__all__ = ["hotmart_negotiation_preview_app"]
