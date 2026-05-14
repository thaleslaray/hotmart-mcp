# Hotmart no Claude

Conecta o Claude direto na sua conta Hotmart. Aí você pergunta em português normal e o Claude busca, cria cupom, cancela assinatura, gera relatório — sem você abrir o painel.

**Exemplo:**

> Você: *"quanto vendi esse mês comparado ao passado?"*
>
> Claude: vai na Hotmart, puxa os números dos 2 meses, monta a comparação e te entrega — em segundos.

---

## Como instalar

### Se você usa Claude Desktop (Mac/Windows)

1. **Baixa o arquivo:** [hotmart.mcpb](https://github.com/thaleslaray/hotmart-mcp/releases/latest) (vai abrir a página da release — o arquivo `.mcpb` tá no final)
2. **Duplo-clique** no arquivo baixado
3. O Claude Desktop abre uma janela perguntando se quer instalar — clica **Instalar**
4. Ele vai pedir 3 dados da sua Hotmart (a gente pega eles no próximo passo)

### Se você usa Claude Code (terminal)

Digita esses 3 comandos no Claude Code:

```
/plugin marketplace add thaleslaray/plugins
/plugin install hotmart
/hotmart:configure
```

---

## Como pegar suas credenciais da Hotmart

São 3 valores que a Hotmart te dá pra "abrir a porta" entre o Claude e sua conta.

1. **Entra em** [app-vlc.hotmart.com/tools/credentials](https://app-vlc.hotmart.com/tools/credentials) (logado na sua conta Hotmart)

2. Clica em **Criar Credencial**

3. Dá um nome qualquer (ex: "Claude") e confirma. **Deixa "Sandbox" desmarcado** se quer usar com dados reais.

4. Abre a credencial criada. Você vai ver 3 campos pra copiar:
   - `Client ID`
   - `Client Secret`
   - `Basic`

5. Cola os 3 valores no Claude quando ele pedir.

⚠️ **Nunca compartilha esses valores.** Quem tiver eles consegue mexer na sua conta Hotmart inteira — ver vendas, criar cupom, cancelar assinatura.

---

## O que você pode pedir pro Claude

Depois de instalar e configurar, é só conversar em português normal. Alguns exemplos do que ele consegue fazer:

### 💰 Sobre suas vendas

- *"quanto vendi mês passado?"*
- *"lista as vendas de outubro do produto X"*
- *"quem comprou nas últimas 24 horas?"*
- *"detalhe das comissões que recebi como coproducer no último trimestre"*
- *"estorna a venda HP2890253164"* (cuidado — é destrutivo)

### 🔁 Sobre suas assinaturas

- *"lista as assinaturas ativas dos meus produtos"*
- *"quantos assinantes eu tenho por status (ativos, cancelados, atrasados)?"*
- *"histórico de pagamento do assinante VRWIQQRG"*
- *"cancela a assinatura VRWIQQRG"* ⚠️
- *"cancela essas 50 assinaturas em lote: ABC, DEF, GHI..."* ⚠️
- *"muda o vencimento da assinatura VRWIQQRG pro dia 10"*

### 🎓 Sobre sua área de membros (Club)

- *"quais módulos eu tenho na minha área de membros?"*
- *"lista os alunos cadastrados"*
- *"o aluno V7yQbq3z7J completou quantas aulas?"*

### 📦 Sobre seus produtos

- *"lista todos os meus produtos"*
- *"quais ofertas (preços, descontos) tem o produto X?"*
- *"quais planos de assinatura existem pro produto Y?"*

### 🎟️ Sobre cupons

- *"cria um cupom de 10% pro produto X com código BLACK10"*
- *"lista os cupons ativos do produto X"*
- *"apaga o cupom de id 99999"* ⚠️

### 🎫 Sobre eventos (com ingresso)

- *"informações do evento 5655136 — datas, lotes, etc"*
- *"quem comprou ingresso pro evento 5655136?"*

### 💳 Sobre negociação de inadimplentes

- *"o aluno tá inadimplente — gera uma proposta parcelada com 30% de desconto"*

---

## Coisas pra você saber antes de usar

### 1. Pra área de membros, precisa do "subdomain"

Quando você pergunta sobre módulos, alunos, ou aulas, o Claude precisa saber **qual** área de membros é. O "subdomain" é o nome que aparece na URL pública:

> `hotmart.com/club/`**`afantasticafabricadasautomacoes`**

A parte em negrito é o subdomain. Veja em **Configurações → URL personalizada** no painel do seu Club. Quando o Claude perguntar, é isso que você cola.

### 2. Eventos só funcionam pra "ETICKET"

Se seu produto é um **evento com ingresso vendido** (tipo workshop presencial, show), funciona normal. Se é um **curso ao vivo gravado** (ONLINE_EVENT), as ferramentas de evento não pegam — use as de produtos/vendas no lugar.

### 3. Vendas estornadas e assinaturas canceladas não voltam

Quando você pede pro Claude estornar uma venda ou cancelar uma assinatura, **ele faz na hora**. Não tem "desfazer". Confere antes de mandar.

### 4. Se uma pergunta sua não voltar nada

Pode ser que aquele produto/conta não tem dado cadastrado pra aquilo. Exemplo: pediu "ofertas do produto X" e voltou vazio — significa que esse produto não tem ofertas configuradas no painel (e não que tá com bug).

### 5. Pra atualizar pra versão nova

**Claude Desktop:**
1. Vai em **Configurações → Desenvolvedor → Extensões**
2. Desinstala o Hotmart antigo
3. Baixa o `.mcpb` novo aqui: [releases mais recentes](https://github.com/thaleslaray/hotmart-mcp/releases/latest)
4. Duplo-clique

**Claude Code:**
```
/plugin update hotmart
/reload-plugins
```
E reinicia o Claude Code.

---

## Algo deu errado?

| Mensagem que apareceu | O que fazer |
|---|---|
| **"Missing HOTMART_CLIENT_ID"** ou erro de autenticação | Suas credenciais não foram salvas certo. No Claude Code, roda `/hotmart:configure` de novo. No Desktop, desinstala e reinstala. |
| **"[401] Authentication failed"** | Credenciais erradas ou foram revogadas. Cria credencial nova em [app-vlc.hotmart.com/tools/credentials](https://app-vlc.hotmart.com/tools/credentials) e atualiza no Claude. |
| **"[500] internal_error"** numa pergunta específica | Pode ser bug temporário da API da Hotmart, ou aquele recurso não tem dados, ou sua credencial não tem acesso àquela área. Tenta pedir outra coisa pra ver se é específico. |
| **Claude chamou a ferramenta errada** (puxou venda quando você queria assinatura) | Reformula a pergunta sendo mais específico. Se persistir, abre uma [issue](https://github.com/thaleslaray/hotmart-mcp/issues) com a pergunta exata — eu uso isso pra melhorar. |

---

## Privacidade e segurança

- **Suas credenciais ficam só no seu computador**, num arquivo de configuração local. Não passam por servidor meu nem da Anthropic.
- **O Claude se conecta direto na API oficial da Hotmart** (`developers.hotmart.com`) usando suas credenciais. Não tem intermediário.
- Se você revogar as credenciais no painel Hotmart, o Claude para de funcionar imediatamente.

---

## Pra quem é desenvolvedor

Se você quer entender o que tá por baixo, modificar, contribuir, ou rodar em outros clientes MCP (Cursor, Cline, etc):

- **Source code:** este repo
- **Documentação técnica:** [`CLAUDE.md`](CLAUDE.md)
- **OpenAPI spec:** [`specs/hotmart-api.json`](specs/hotmart-api.json)
- **Eval framework:** [`scripts/build_eval.py`](scripts/build_eval.py) + [`scripts/test_all_gets.py`](scripts/test_all_gets.py) — 98.4% both-correct em 840 prompts PT-BR

```bash
pip install git+https://github.com/thaleslaray/hotmart-mcp.git
# ou via uvx no .mcp.json
```

Configuração via env vars (`HOTMART_CLIENT_ID`, `HOTMART_CLIENT_SECRET`, `HOTMART_BASIC_AUTH`) ou JSON em `~/.config/hotmart/config.json`.

PRs e issues bem-vindos: [issues](https://github.com/thaleslaray/hotmart-mcp/issues).

---

## Licença

MIT — feito por [Thales Laray](https://instagram.com/thaleslaray)
