# hotmart-mcp

Plugue o Claude (ou qualquer cliente MCP) na sua conta Hotmart. Vendas, assinaturas, área de membros, produtos, cupons.

## Instalar

```bash
pip install git+https://github.com/thaleslaray/hotmart-mcp.git
```

## Configurar

1. Pega suas credenciais em [developers.hotmart.com](https://developers.hotmart.com) → criar app → copia `Client ID`, `Client Secret` e `Basic`.
2. Cola no `.mcp.json` (ou `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "hotmart": {
      "command": "hotmart-mcp",
      "env": {
        "HOTMART_CLIENT_ID": "cole_aqui",
        "HOTMART_CLIENT_SECRET": "cole_aqui",
        "HOTMART_BASIC_AUTH": "cole_aqui"
      }
    }
  }
}
```

3. Reinicia o Claude. Pronto.

## O que dá pra fazer

Pergunta em português normal:

- "Quanto vendi mês passado?"
- "Lista as assinaturas que cancelaram essa semana"
- "Cria um cupom de 20% pro produto X"
- "Quem assistiu mais de 80% do módulo Y?"
- "Estorna a venda HP12345"

## Problemas?

Abra uma [issue](https://github.com/thaleslaray/hotmart-mcp/issues).

## Licença

MIT
