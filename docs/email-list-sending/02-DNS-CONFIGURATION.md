# Configuração DNS - Autenticação de Email

## Importância Crítica

**Sem SPF, DKIM e DMARC configurados corretamente, seus emails irão DIRETO para spam**, independentemente do conteúdo.

Estes protocolos provam aos provedores de email que:
1. Você é quem diz ser (autenticação)
2. Seus emails não foram alterados (integridade)
3. Você é um remetente legítimo (reputação)

---

## 1. SPF (Sender Policy Framework)

### O Que É
SPF autoriza quais servidores podem enviar emails pelo seu domínio.

### Configuração

**Adicionar registro TXT no DNS do domínio**:

```dns
v=spf1 include:spf.antispamcloud.com a mx ~all
```

### Explicação dos Componentes:
- `v=spf1` - Versão do protocolo
- `include:spf.antispamcloud.com` - Autoriza servidores SpamExperts
- `a` - Autoriza servidor A record do domínio
- `mx` - Autoriza servidores MX do domínio
- `~all` - Soft fail para outros servidores

### Validação

```bash
# Verificar SPF configurado
dig TXT alitools.pt | grep spf

# Ou usar ferramenta online
# https://mxtoolbox.com/spf.aspx
```

---

## 2. DKIM (DomainKeys Identified Mail)

### O Que É
DKIM assina digitalmente seus emails para verificar que não foram alterados em trânsito.

### Configuração

**Passo 1: Gerar Chave DKIM**

No cPanel ou provider SMTP:
1. Aceder gestão de email
2. Procurar "DKIM" ou "Email Authentication"
3. Gerar nova chave DKIM
4. Copiar registro DNS fornecido

**Passo 2: Adicionar ao DNS**

Exemplo de registro (formato varia):

```dns
default._domainkey.alitools.pt TXT "v=DKIM1; k=rsa; p=MIGfMA0GCS..."
```

### Validação

```bash
# Verificar DKIM configurado
dig TXT default._domainkey.alitools.pt

# Ou usar ferramenta online
# https://mxtoolbox.com/dkim.aspx
```

**Teste de Envio**:
1. Enviar email para check-auth@verifier.port25.com
2. Receber relatório detalhado de autenticação

---

## 3. DMARC (Domain-based Message Authentication)

### O Que É
DMARC define política de como tratar emails que falham SPF/DKIM e fornece relatórios.

### Configuração - Fase 1 (Monitorização)

**Adicionar registro TXT no DNS**:

```dns
_dmarc.alitools.pt TXT "v=DMARC1; p=none; rua=mailto:postmaster@alitools.pt"
```

### Explicação:
- `v=DMARC1` - Versão do protocolo
- `p=none` - Política: apenas monitorizar (não bloquear)
- `rua=mailto:...` - Email para receber relatórios agregados

### Evolução da Política

**Após 2-4 semanas com `p=none` e métricas boas**:

```dns
# Fase 2: Quarentena (emails suspeitos vão para spam)
_dmarc.alitools.pt TXT "v=DMARC1; p=quarantine; pct=10; rua=mailto:postmaster@alitools.pt"

# Fase 3: Rejeição (apenas após confiança total)
_dmarc.alitools.pt TXT "v=DMARC1; p=reject; rua=mailto:postmaster@alitools.pt"
```

### Validação

```bash
# Verificar DMARC configurado
dig TXT _dmarc.alitools.pt

# Ou usar ferramenta online
# https://mxtoolbox.com/dmarc.aspx
```

---

## 4. Configuração no cPanel Dominios.pt

### Passo a Passo

**1. Aceder Zona DNS**
```
cPanel > Zonas DNS > Gerir > alitools.pt
```

**2. Adicionar Registros**

Para cada registro (SPF, DKIM, DMARC):
- Tipo: TXT
- Nome: conforme especificado acima
- TTL: 14400 (4 horas)
- Valor: texto completo do registro

**3. Salvar e Aguardar Propagação**
- Tempo de propagação: 1-24 horas
- Verificar após 2 horas

---

## 5. Validação Completa

### Checklist de Verificação

```bash
#!/bin/bash
# Script de validação completa

DOMAIN="alitools.pt"

echo "=== Validando Configuração DNS ==="
echo ""

echo "[SPF]"
dig TXT $DOMAIN +short | grep spf

echo ""
echo "[DKIM]"
dig TXT default._domainkey.$DOMAIN +short

echo ""
echo "[DMARC]"
dig TXT _dmarc.$DOMAIN +short

echo ""
echo "=== Fim da Validação ==="
```

### Ferramentas Online de Teste

1. **MXToolbox SuperTool**: https://mxtoolbox.com/SuperTool.aspx
   - Testa SPF, DKIM, DMARC, Blacklists
   
2. **Mail-Tester**: https://www.mail-tester.com/
   - Score de spam completo (alvo: 10/10)
   
3. **Google Admin Toolbox**: https://toolbox.googleapps.com/apps/checkmx/
   - Valida configuração MX e autenticação

---

## 6. Teste de Envio Real

### Procedimento

**1. Enviar Email de Teste**

```python
# Via SendCraft API
import requests

response = requests.post(
    'http://localhost:5000/api/v1/send-direct',
    headers={'Authorization': 'Bearer YOUR_API_KEY'},
    json={
        'domain': 'alitools.pt',
        'account': 'encomendas',
        'to': 'check-auth@verifier.port25.com',
        'subject': 'Teste Autenticação DNS',
        'html': '<h1>Teste SPF/DKIM/DMARC</h1>',
        'text': 'Teste SPF/DKIM/DMARC'
    }
)
```

**2. Analisar Relatório Recebido**

Verificar:
- ✅ SPF: PASS
- ✅ DKIM: PASS
- ✅ DMARC: PASS

---

## 7. Manutenção Contínua

### Monitorização Mensal

- Verificar relatórios DMARC recebidos
- Validar que nenhum servidor não autorizado está enviando
- Ajustar política DMARC conforme necessário

### Alertas Importantes

🚨 **Renovar atenção se**:
- Alterar servidor SMTP
- Adicionar novo domínio
- Mudar provedor de email
- Taxa de falha DMARC > 5%

---

## Resultado Esperado

Com configuração correta:
- ✅ Emails passam autenticação SPF
- ✅ Emails passam verificação DKIM
- ✅ Política DMARC aplicada
- ✅ Score Mail-Tester: 9-10/10
- ✅ Deliverability maximizada

---

**Próximo Passo**: [Sistema de Listas](03-LIST-MANAGEMENT.md) - Implementar gestão de contactos
