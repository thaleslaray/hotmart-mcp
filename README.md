# hotmart-mcp

Plugue o Claude (ou qualquer cliente MCP) na sua conta Hotmart. **28 tools** auto-geradas da spec OpenAPI oficial cobrindo vendas, assinaturas, área de membros, produtos, cupons, eventos e negociação.

✅ **98.4% both-correct** medido em 840 prompts PT-BR realistas (3 personas × 28 tools × 10 variations).

---

## Instalação

### Claude Code (terminal)

```
/plugin marketplace add thaleslaray/plugins
/plugin install hotmart
/hotmart:configure
```

### Claude Desktop

Baixa o `.mcpb` na [release mais recente](https://github.com/thaleslaray/hotmart-mcp/releases/latest) e dá duplo-clique.

### Cursor / Cline / outros clientes MCP

Cola no `.mcp.json` ou `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "hotmart": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/thaleslaray/hotmart-mcp.git", "hotmart-mcp"],
      "env": {
        "HOTMART_CLIENT_ID": "...",
        "HOTMART_CLIENT_SECRET": "...",
        "HOTMART_BASIC_AUTH": "..."
      }
    }
  }
}
```

---

## Configurar credenciais

1. Acessa [app-vlc.hotmart.com/tools/credentials](https://app-vlc.hotmart.com/tools/credentials)
2. **Criar Credencial** → dá um nome → confirma (deixa Sandbox desmarcado pra produção)
3. Abre a credencial criada → copia `Client ID`, `Client Secret` e `Basic`
4. Cola nos 3 campos durante `/hotmart:configure` (Claude Code) ou no `.mcpb` installer (Desktop)

O server lê credenciais nesta ordem de precedência:
1. Variáveis de ambiente (`HOTMART_CLIENT_ID`, etc) — uso típico em `.mcp.json` com bloco `env`
2. `~/.config/hotmart/config.json` — XDG, cross-client (Cursor, Cline, Desktop, Code)
3. `~/.claude/plugins/data/hotmart/config.json` — onde o `/hotmart:configure` do Claude Code salva
4. `src/hotmart_mcp/.env.json` — dev local

Formato do JSON:
```json
{
  "HOTMART_CLIENT_ID": "...",
  "HOTMART_CLIENT_SECRET": "...",
  "HOTMART_BASIC_AUTH": "..."
}
```

---

## Como usar — exemplos por área

Depois de configurar, pergunta em português normal. Claude escolhe a tool certa.

### 📊 Vendas

| Pergunta | Tool chamada |
|---|---|
| "Quanto vendi mês passado?" | `hotmart_sales_summary_list` |
| "Lista as vendas de outubro do produto 4168346" | `hotmart_sales_history_list` |
| "Quem comprou nas últimas 24h?" | `hotmart_sales_participants_list` |
| "Comissões CO_PRODUCER de Q4 2024" | `hotmart_sales_commissions_list` |
| "Detalhe de preço (impostos, taxas) das últimas vendas" | `hotmart_sales_price_details_list` |
| "Estorna a venda HP2890253164" | `hotmart_sale_refund` ⚠️ destrutivo |

### 🔁 Assinaturas

| Pergunta | Tool |
|---|---|
| "Lista as assinaturas ativas dos meus produtos" | `hotmart_subscriptions_list` |
| "Quantas assinaturas tenho por status?" | `hotmart_subscriptions_summary_list` |
| "Histórico de pagamentos dos meus assinantes" | `hotmart_subscription_transactions_list` |
| "Compras do assinante VRWIQQRG" | `hotmart_subscriber_purchases_list` |
| "Cancela a assinatura VRWIQQRG" | `hotmart_subscription_cancel` ⚠️ |
| "Cancela essas 50 assinaturas em lote" | `hotmart_batch_subscriptions_cancel` ⚠️ |
| "Reativa a assinatura VRWIQQRG" | `hotmart_subscription_reactivate` |
| "Reativa essas 30 assinaturas todas" | `hotmart_batch_subscriptions_reactivate` |
| "Muda o vencimento de VRWIQQRG pro dia 10" | `hotmart_subscription_due_day_update` |

### 🎓 Club (área de membros)

| Pergunta | Tool |
|---|---|
| "Quais módulos tenho no meu Club?" | `hotmart_modules_list` |
| "Páginas/aulas do módulo X" | `hotmart_module_pages_list` |
| "Lista os alunos cadastrados" | `hotmart_students_list` |
| "Progresso do aluno V7yQbq3z7J" | `hotmart_student_progress_get` |

⚠️ **Subdomain obrigatório.** É o slug que aparece na URL pública: `hotmart.com/club/<slug>`. Não é o domínio customizado.

### 📦 Produtos

| Pergunta | Tool |
|---|---|
| "Lista todos os meus produtos" | `hotmart_products_list` |
| "Quais ofertas tem o produto 4168346?" | `hotmart_product_offers_list` |
| "Quais planos tem o produto 4168346?" | `hotmart_product_plans_list` |

### 🎟️ Cupons

| Pergunta | Tool |
|---|---|
| "Cria cupom de 10% pro produto 4168346 código BLACK10" | `hotmart_coupon_create` |
| "Lista cupons do produto 4168346" | `hotmart_coupons_list` |
| "Apaga o cupom de id 99999" | `hotmart_coupon_delete` ⚠️ |

⚠️ Discount vai como **fração** (0.10 = 10%), não percentual (10 ≠ 10%).

### 🎫 Eventos / Tickets

| Pergunta | Tool |
|---|---|
| "Informações do evento 5655136" | `hotmart_event_info_get` |
| "Quem comprou ingresso pro evento 5655136?" | `hotmart_event_participants_list` |

⚠️ Funciona **apenas pra produtos formato ETICKET**, não ONLINE_EVENT (que é curso ao vivo).

### 💰 Negociação

| Pergunta | Tool |
|---|---|
| "Negocia parcelado pro inadimplente SUB11223 com 30% off" | `hotmart_negotiation_generate` |

---

## Caveats importantes

### 1. Datas são timestamps em **milissegundos** (não segundos, não ISO)

Quando você pedir "vendas de outubro 2024", Claude converte pra `1727740800000` automaticamente. Se passar manualmente:

```python
import datetime
start_date = int(datetime.datetime(2024, 10, 1).timestamp() * 1000)  # 1727740800000
```

### 2. Enums são **case-sensitive em INGLÊS**

| ❌ Não funciona | ✅ Funciona |
|---|---|
| `boleto` ou `BOLETO` | `BILLET` |
| `pix` ou `Pix` | `PIX` |
| `aprovada` ou `Approved` | `APPROVED` |
| `cancelada` | `CANCELLED` (2 L) |

A API é em inglês — Claude faz a tradução automática, mas se errar, é por isso.

### 3. Club exige **subdomain do path da URL**

Não é o domínio customizado (`membros.seusite.com.br`). É o slug que aparece em `hotmart.com/club/<slug>`. Veja em **Configurações → URL personalizada** no painel.

### 4. `get_product_offers` / `get_product_plans` retornam vazio se produto não tem oferta/plano cadastrado

Não é bug — significa que aquele produto específico não tem ofertas/planos no painel.

### 5. Eventos só funcionam pra formato ETICKET

Produtos formato `ONLINE_EVENT` (curso ao vivo) **não** são reconhecidos pela API de events/tickets. Use apenas `ETICKET` (eventos com ingressos).

---

## 28 tools cobertas

- **Sales (6):** history_list, summary_list, participants_list, commissions_list, price_details_list, sale_refund
- **Subscriptions (9):** subscriptions_list, summary_list, transactions_list, subscriber_purchases_list, subscription_cancel, batch_subscriptions_cancel, subscription_reactivate, batch_subscriptions_reactivate, subscription_due_day_update
- **Club (4):** modules_list, module_pages_list, students_list, student_progress_get
- **Products (3):** products_list, product_offers_list, product_plans_list
- **Coupons (3):** coupon_create, coupons_list, coupon_delete
- **Tickets (2):** event_info_get, event_participants_list
- **Negotiation (1):** negotiation_generate

Todas auto-geradas a partir de [`specs/hotmart-api.json`](specs/hotmart-api.json) (OpenAPI 3.0.3 oficial Hotmart).

---

## Troubleshooting

### "Missing HOTMART_CLIENT_ID"

Credenciais não encontradas. Verifica os 4 caminhos de fallback (env vars + 3 JSONs). Em Claude Code, roda `/hotmart:configure` de novo.

### "[500] internal_error" em uma tool

Pode ser:
- **API da Hotmart com bug naquele endpoint** (já aconteceu com `/offers` e `/plans` — corrigido na v0.1.1 com fix da spec)
- **Produto sem dados cadastrados** (ex: sem ofertas → vazio, mas alguns retornam 500 em vez de array vazio)
- **Auth scope insuficiente** — confere que a credencial tem acesso ao recurso (Vendas, Assinaturas, Club, etc) no painel

### "[401] Authentication failed"

Credenciais erradas ou expiradas. Re-cria em [app-vlc.hotmart.com/tools/credentials](https://app-vlc.hotmart.com/tools/credentials) e atualiza o config.

### Tool errada chamada

Abre uma [issue](https://github.com/thaleslaray/hotmart-mcp/issues) com:
- Prompt exato que você usou
- Tool que Claude chamou
- Tool que deveria ter chamado

Esses casos são alimentados no eval framework (3 personas × 280 prompts) pra calibrar o próximo bump.

### Como atualizar pra versão nova

**Claude Code:**
```
/plugin update hotmart
rm -rf ~/.cache/uv/git-v0/checkouts/*hotmart*
/reload-plugins
```
Reinicia Claude Code.

**Claude Desktop:**
1. Settings → Developer → Extensions → desinstalar versão antiga
2. Baixa novo `.mcpb` da [release](https://github.com/thaleslaray/hotmart-mcp/releases/latest)
3. Duplo-clique

---

## Arquitetura

```
specs/hotmart-api.json     ← OpenAPI 3.0.3 oficial (fonte da verdade)
        ↓
src/hotmart_mcp/generator.py    ← code-gen
        ↓
src/hotmart_mcp/tools/*.py      ← 28 tools auto-geradas (não editar à mão)
        ↓
FastMCP server (src/hotmart_mcp/server.py)
        ↓
Claude / Cursor / Cline / qualquer client MCP
```

Mais detalhes técnicos em [`CLAUDE.md`](CLAUDE.md).

---

## Issues / contribuições

Issues, bug reports e prompts realistas em PT-BR que confundem o LLM são bem-vindos: [issues](https://github.com/thaleslaray/hotmart-mcp/issues).

## Licença

MIT
