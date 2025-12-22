# Configuração DNS - Autenticação de Email

## Importância

**Sem SPF, DKIM e DMARC configurados corretamente, praticamente 100% dos emails serão marcados como spam.**

Estes três protocolos são a base da autenticação de email moderna e são verificados por todos os grandes provedores (Gmail, Outlook, Yahoo, etc.).

## 1. SPF (Sender Policy Framework)

### O Que É

SPF autoriza quais servidores podem enviar emails em nome do seu domínio.

### Como Configurar

**Passo 1**: Aceder ao painel DNS do domínio

**Passo 2**: Criar registo TXT:

```
Nome: @ (ou domínio raiz)
Tipo: TXT
Valor: v=spf1 include:spf.antispamcloud.com a mx ~all
```

### Explicação do Registo

- `v=spf1` - Versão do protocolo
- `include:spf.antispamcloud.com` - Incluir SPF do provider de email
- `a` - Autorizar servidor A record
- `mx` - Autorizar servidores MX
- `~all` - Soft fail para outros servidores (recomendado para início)

### Validação

```bash
# Via terminal
dig TXT [SEU-DOMINIO] +short

# Ou usar ferramenta online
https://mxtoolbox.com/spf.aspx
```

**Resultado esperado**: O registo SPF deve aparecer

---

## 2. DKIM (DomainKeys Identified Mail)

### O Que É

DKIM adiciona uma assinatura digital criptográfica a cada email, permitindo que o destinatário verifique que o email não foi alterado e vem realmente do domínio declarado.

### Como Configurar

**Passo 1**: Gerar chave DKIM no provider SMTP

**No cPanel**:
1. Email → Email Deliverability
2. Selecionar domínio
3. Clicar em "Manage" → "Install the suggested DKIM keys"
4. Copiar a chave pública gerada

**Passo 2**: Adicionar registo DNS

```
Nome: default._domainkey.[SEU-DOMINIO]
Tipo: TXT
Valor: v=DKIM1; k=rsa; p=[CHAVE-PUBLICA-GERADA]
```

### Validação

```bash
dig TXT default._domainkey.[SEU-DOMINIO] +short
```

**Testar envio**:
1. Enviar email para si próprio
2. Ver headers do email recebido
3. Procurar por `DKIM-Signature:` - deve estar presente
4. Gmail mostra "signed-by: [seu-dominio]" se válido

---

## 3. DMARC (Domain-based Message Authentication)

### O Que É

DMARC instrui os destinatários sobre o que fazer com emails que falham SPF ou DKIM, e envia relatórios sobre autenticação.

### Como Configurar

**Passo 1**: Criar registo DNS

```
Nome: _dmarc.[SEU-DOMINIO]
Tipo: TXT
Valor: v=DMARC1; p=none; rua=mailto:postmaster@[SEU-DOMINIO]; ruf=mailto:postmaster@[SEU-DOMINIO]; fo=1
```

### Explicação do Registo

- `v=DMARC1` - Versão do protocolo
- `p=none` - Política (none = monitorização apenas)
- `rua=` - Email para relatórios agregados
- `ruf=` - Email para relatórios forenses
- `fo=1` - Enviar relatório se qualquer verificação falhar

### Evolução da Política

**Fase 1 - Warm-up (Semanas 1-2)**:
```
p=none
```
Apenas monitorizar, não aplicar política

**Fase 2 - Validação (Semanas 3-4)**:
```
p=quarantine; pct=10
```
Quarentena 10% dos emails que falham

**Fase 3 - Produção (Após Semana 4)**:
```
p=quarantine; pct=100
```
Quarentena todos os emails que falham

**Fase 4 - Máxima Segurança (Após 2 meses)**:
```
p=reject
```
Rejeitar completamente emails que falham

### Validação

```bash
dig TXT _dmarc.[SEU-DOMINIO] +short
```

---

## Ferramentas de Validação Completa

### 1. MXToolbox
```
https://mxtoolbox.com/SuperTool.aspx
```
- Validar SPF, DKIM, DMARC
- Verificar blacklists
- Testar DNS

### 2. Mail-Tester
```
https://www.mail-tester.com/
```
1. Enviar email de teste para o endereço fornecido
2. Receber score de 0-10
3. **Objetivo**: Score ≥ 8/10

### 3. Google Admin Toolbox
```
https://toolbox.googleapps.com/apps/messageheader/
```
- Analisar headers de email
- Validar autenticação

### 4. DMARC Analyzer
```
https://dmarcreport.com/
```
- Monitorizar relatórios DMARC
- Visualizar falhas de autenticação

---

## Checklist de Validação DNS

**Antes de iniciar warm-up, verificar**:

- [ ] SPF configurado e validado
- [ ] DKIM gerado e configurado
- [ ] DMARC configurado (iniciar com p=none)
- [ ] Mail-Tester score ≥ 8/10
- [ ] MXToolbox sem alertas críticos
- [ ] Não aparecer em blacklists
- [ ] Reverse DNS (PTR) configurado
- [ ] Propagação DNS completa (24-48h)

---

## Troubleshooting

### SPF Falha

**Problema**: "SPF record not found"

**Solução**:
1. Verificar se registo TXT está correto
2. Aguardar propagação DNS (até 48h)
3. Testar com `dig TXT dominio.com`

### DKIM Falha

**Problema**: "DKIM signature verification failed"

**Solução**:
1. Verificar se chave pública no DNS corresponde à privada
2. Regenerar chave se necessário
3. Verificar selector (default._domainkey)

### DMARC Não Recebe Relatórios

**Problema**: Email `rua=` não recebe relatórios

**Solução**:
1. Verificar se email de destino existe
2. Aguardar 24-48h (relatórios são enviados diariamente)
3. Verificar spam do email de relatórios

---

## Próximos Passos

Após configuração DNS completa:
1. **Aguardar 24-48h** para propagação completa
2. **Validar com todas as ferramentas** acima
3. **Fazer teste de envio** para Gmail/Outlook
4. **Proceder para** [02-TEMPLATE-OTIMIZADO.md](./02-TEMPLATE-OTIMIZADO.md)

---

**Nota Crítica**: Não iniciar warm-up sem ter DNS 100% configurado e validado. É perda de tempo e prejudica reputação.
