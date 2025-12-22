# Construção de Reputação de Email

## O Que é Reputação de Email?

Reputação de email é a **"nota"** que provedores (Gmail, Outlook, Yahoo) e sistemas anti-spam dão ao seu domínio e IP baseado no comportamento de envio.

### Como é Calculada?

Provedores analisam centenas de sinais:

**Sinais Positivos** (⬆️ Aumentam reputação):
- Emails abertos e lidos
- Respostas dos destinatários
- Emails movidos para inbox (se estavam em spam)
- Baixa taxa de bounce
- Autenticação correcta (SPF/DKIM/DMARC)
- Volume consistente e gradual
- Engage (cliques, forwards)

**Sinais Negativos** (⬇️ Destroem reputação):
- Emails deletados sem ler
- Marcados como spam
- Alto bounce rate
- Reclamações de spam
- Volume errático (0 emails por semanas, depois 5000 de repúblico)
- Autenticação falhada
- Spam traps (emails armadilha)

### Escala de Reputação

```
100-90: Excelente → Inbox principal, máxima deliverability
 89-70: Boa      → Inbox, deliverability sólida  
 69-50: Média   → Alguns emails para promoções/spam
 49-30: Fraca    → Maioria vai para spam
 29-0:  Péssima → Bloqueado, blacklist
```

---

## Pilares da Boa Reputação

### 1. Autenticação DNS (Fundamental)

#### SPF (Sender Policy Framework)
**O que faz**: Autoriza quais servidores podem enviar emails pelo seu domínio.

**Configuração**:
```dns
Tipo: TXT
Nome: @
Valor: v=spf1 include:spf.antispamcloud.com a mx ~all
```

**Sem SPF**: 70% dos emails vão para spam.

#### DKIM (DomainKeys Identified Mail)
**O que faz**: Assina digitalmente os emails para verificar autenticidade.

**Configuração**:
```dns
Tipo: TXT
Nome: default._domainkey
Valor: [Chave gerada pelo provider SMTP]
```

**Sem DKIM**: Falta de confiança, maior risco de spam.

#### DMARC (Domain-based Message Authentication)
**O que faz**: Define política de o que fazer se SPF/DKIM falharem.

**Configuração inicial**:
```dns
Tipo: TXT
Nome: _dmarc
Valor: v=DMARC1; p=none; rua=mailto:postmaster@seudominio.pt
```

**Evolução**:
- **Fase 1**: `p=none` (monitorizar apenas)
- **Fase 2**: `p=quarantine` (emails suspeitos para spam)
- **Fase 3**: `p=reject` (rejeitar emails não autenticados)

⚠️ **CRÍTICO**: Sem estas 3 configurações, warm-up não funciona!

---

### 2. Qualidade de Conteúdo

#### Rcio Texto vs Imagens

**Ideal**: 60-70% texto, 30-40% imagens

| Template | Texto | Imagens | Deliverability | Risco Spam |
|----------|-------|---------|----------------|-----------|
| Ultra-simples | 80% | 20% | 95-98% | Muito Baixo |
| Híbrido | 65% | 35% | 85-90% | Baixo |
| Image-heavy | 40% | 60% | 60-70% | Alto |
| Image-only | 0% | 100% | 40-50% | Muito Alto |

#### Estrutura Ideal de Email

```html
<!-- BOM -->
<body>
  <div style="max-width: 600px;">
    <h1>Título Principal</h1>
    
    <p>Parágrafo de texto real HTML...</p>
    <p>Mais texto com valor...</p>
    
    <!-- Imagem pequena com alt text -->
    <img src="logo.png" alt="Logo AliTools" 
         style="width:120px; height:80px;">
    
    <p>Mais conteúdo texto...</p>
    
    <!-- Botão HTML, não imagem -->
    <a href="link" style="background: #0066cc; 
                           color: white; 
                           padding: 12px 24px;">
      Botão Texto
    </a>
    
    <p>Footer com unsubscribe</p>
  </div>
</body>

<!-- MAU -->
<body>
  <img src="flyer-completo.jpg" width="600">
</body>
```

#### Palavras/Frases a Evitar

**Spam Triggers** (❌ Nunca usar):
- "GRÁTIS", "100% GRATUÍTO"
- "Clique AQUI AGORA!!!"
- "Ganhar dinheiro rápido"
- "Urgente!!!", "OPORTUNIDADE ÚNICA"
- MAISÚSCULAS EXCESSIVAS
- Muitos pontos!!!! de exclamação!!!!
- "Parabéns, você ganhou"
- "Sem risco", "Garantido"

**Alternativas Seguras** (✅ Usar):
- "Oferta especial para si"
- "Descubra as novidades"
- "Desconto exclusivo"
- "Bem-vindo à [Marca]"
- "Novidades [Mês]"

#### Assunto do Email

**Boas práticas**:
- ✅ Claro e honesto
- ✅ 30-50 caracteres
- ✅ Personalizado quando possível
- ✅ Sem clickbait

**Exemplos**:
```
✅ "Novidades AliTools - Desconto 5%"
✅ "Bem-vindo ao AliTools.pt, [Nome]"
✅ "Oferta Exclusiva para Si"
❌ "GRATIS!!! CLIQUE AGORA!!!"
❌ "VOCÊ GANHOU UM PRÉMIO"
```

---

### 3. Comportamento Natural de Envio

#### Delays Entre Envios

**Recomendado**: 3 minutos (180 segundos) entre cada email

**Por quê?**
- Simula comportamento humano
- Evita triggers de "bot" dos provedores
- Reduz carga instantânea no servidor SMTP
- Permite monitorizar bounces em tempo real

**Velocidade**:
- 3 min/email = 20 emails/hora
- 20 emails/hora × 10 horas = 200 emails/dia
- 20 emails/hora × 15 horas = 300 emails/dia

#### Consistência de Horários

**Importante**: Enviar sempre no mesmo horário todos os dias.

**Horários Recomendados** (Portugal):
- **Melhor**: 10h-18h (horário comercial)
- **OK**: 9h-20h (horário alargado)
- **Evitar**: 0h-7h, 22h-24h

**Padrão ideal**:
```
Segunda: 10h00 - 18h00
Terça:   10h00 - 18h00
Quarta:  10h00 - 18h00
...
```

#### Volume Crescente Gradual

**Regra**: Aumentar 10-20% por dia (máximo)

```
Dia 1:  50 emails   (baseline)
Dia 2:  50 emails   (manter)
Dia 3:  55 emails   (+10%)
Dia 4:  60 emails   (+9%)
Dia 5:  70 emails   (+17%)
Dia 6:  75 emails   (+7%)
Dia 7:  85 emails   (+13%)
```

❌ **Nunca fazer**:
```
Dia 1:  50 emails
Dia 2: 500 emails  (10x aumento - DESASTRE!)
```

---

### 4. Qualidade da Lista de Emails

#### Emails Válidos

**Obrigatório**: Lista deve ter emails válidos e activos.

**Sinais de lista boa**:
- ✅ Emails obtidos de forma legítima (opt-in)
- ✅ Confirmados/validados
- ✅ Bounce rate histórico < 2%
- ✅ Sem spam traps

**Sinais de lista problemática**:
- ❌ Comprada/alugada
- ❌ Scraping de websites
- ❌ Emails antigos (5+ anos)
- ❌ Bounce rate > 5%

#### Validar Lista Antes de Enviar

**Serviços recomendados**:
- [NeverBounce](https://neverbounce.com/)
- [ZeroBounce](https://www.zerobounce.net/)
- [EmailListVerify](https://www.emaillistverify.com/)

**O que validam**:
- Email existe?
- Caixa de correio activa?
- É spam trap?
- Domínio válido?

#### Remover Bounces Imediatamente

**Hard bounces** (permanentes):
- Email não existe
- Domínio inválido
- Caixa de correio inexistente

**Ação**: Remover da lista **imediatamente** após primeiro bounce.

---

### 5. Monitorização Contínua

#### Métricas Crticas

##### Taxa de Bounce

**Meta**: < 2%  
**Alerta**: 2-5%  
**Crítico**: > 5%

**Cálculo**:
```
Bounce Rate = (Bounces / Enviados) × 100

Exemplo:
500 enviados, 8 bounces
Bounce Rate = (8 / 500) × 100 = 1.6% (✅ BOM)
```

**Acções**:
- < 2%: Continuar normalmente
- 2-5%: Reduzir volume 30%, validar lista
- > 5%: **PARAR**, limpar lista, reiniciar warm-up

##### Taxa de Abertura (Open Rate)

**Meta**: > 20%  
**Alerta**: 10-20%  
**Crítico**: < 10%

**Cálculo**:
```
Open Rate = (Opens Únicos / Entregues) × 100

Exemplo:
500 entregues, 110 abertos
Open Rate = (110 / 500) × 100 = 22% (✅ EXCELENTE)
```

**Acções**:
- > 20%: Óptimo, continuar
- 10-20%: Revisar assuntos e conteúdo
- < 10%: Mudanças urgentes necessárias

##### Spam Complaints

**Meta**: < 0.1%  
**Alerta**: 0.1-0.3%  
**Crítico**: > 0.5%

**Cálculo**:
```
Spam Rate = (Complaints / Enviados) × 100

Exemplo:
1000 enviados, 1 complaint
Spam Rate = (1 / 1000) × 100 = 0.1% (✅ LIMITE)
```

**Acções**:
- < 0.1%: Perfeito
- 0.1-0.3%: Revisar conteúdo, adicionar unsubscribe mais visível
- > 0.5%: **PARAR**, investigação completa

#### Ferramentas de Monitorização

##### Google Postmaster Tools
**URL**: https://postmaster.google.com/

**O que monitoriza**:
- Reputação do domínio (High/Medium/Low)
- Taxa de spam
- Feedback loops
- Autenticação (SPF/DKIM)
- Encriptação TLS

**Configurar**: Adicionar e verificar domínio via DNS.

##### MXToolbox Blacklist Check
**URL**: https://mxtoolbox.com/blacklists.aspx

**O que verifica**:
- 100+ blacklists em simultâneo
- Reputação do IP
- Configuração DNS (SPF/DKIM/DMARC)
- Deliverability score

**Uso**: Verificar **diariamente** durante warm-up.

##### Mail-Tester
**URL**: https://www.mail-tester.com/

**O que testa**:
- Spam score (0-10)
- Autenticação DNS
- Qualidade HTML
- Links suspeitos
- Blacklist status

**Uso**: Testar template antes de campanha.

---

### 6. Elementos Obrigatórios no Email

#### Botão Unsubscribe Visível

**Obrigatório por**:
- Lei RGPD (Europa)
- CAN-SPAM Act (EUA)
- Requisito dos provedores

**Implementação**:
```html
<p style="font-size: 12px; color: #666; text-align: center;">
  Não deseja receber estes emails?<br>
  <a href="https://seudominio.pt/unsubscribe?email={{email}}" 
     style="color: #0066cc;">
    Cancelar subscrição
  </a>
</p>
```

**Localização**: Footer do email, sempre visível.

#### Informações da Empresa

**Obrigatório incluir**:
- Nome da empresa
- Morada física completa
- Contacto (email ou telefone)
- NIF/NIPC (recomendado)

**Exemplo**:
```html
<div style="font-size: 11px; color: #999; margin-top: 30px;">
  <strong>AliTools, Lda.</strong><br>
  Rua Exemplo, 123, 1000-001 Lisboa, Portugal<br>
  NIF: 123456789<br>
  Email: geral@alitools.pt | Tel: +351 21 000 0000
</div>
```

#### Texto Alternativo (Plain Text)

**Obrigatório**: Sempre enviar versão plain text além de HTML.

**Por quê?**:
- Clientes de email que bloqueiam HTML
- Acessibilidade (leitores de tela)
- Melhor deliverability

---

## Sinais que Destroem Reputação

### ❌ 1. Spam Traps
**O que são**: Emails armadilha criados por provedores para identificar spammers.

**Como evitar**:
- Usar apenas emails opt-in
- Validar lista antes de enviar
- Nunca comprar listas
- Remover inativos (1+ ano sem abrir)

### ❌ 2. Alto Bounce Rate
**Problema**: > 5% indica lista de má qualidade.

**Impacto**: Reputação desce rapidamente.

### ❌ 3. Reclamações de Spam
**Problema**: Utilizadores marcam como spam.

**Impacto**: Cada reclamação pesa muito negativamente.

### ❌ 4. Volume Errático
**Problema**: 0 emails por semanas, depois 5000 de repúblico.

**Impacto**: Comportamento de spammer típico.

### ❌ 5. Conteúdo Spam
**Problema**: Palavras spam, image-only, links suspeitos.

**Impacto**: Filtros automáticos bloqueiam.

---

## Como Recuperar Reputação Danificada

### Se Entrou em Blacklist

1. **Identificar blacklists**: Via MXToolbox
2. **Corrigir problemas**: SPF/DKIM/DMARC, limpar lista
3. **Seguir processo de remoção**: Cada blacklist tem procedimento próprio
4. **Reduzir volume**: Voltar para 50 emails/dia
5. **Monitorizar**: 2-4 semanas para recuperar

### Se Reputação Baixa

1. **Pausar envios**: 3-7 dias
2. **Validar lista**: Remover inválidos
3. **Melhorar templates**: Mais texto, menos imagens
4. **Recomeçar warm-up**: Início da Semana 1
5. **Monitorizar**: Melhoria gradual 4-8 semanas

---

## Manutenção de Reputação de Longo Prazo

### Ações Mensais
- [ ] Limpar lista (remover inativos 6+ meses)
- [ ] Verificar blacklist status
- [ ] Analisar métricas agregadas
- [ ] Actualizar templates
- [ ] Testar novos assuntos

### Ações Trimestrais
- [ ] Revalidar lista completa
- [ ] Revisar configuração DNS
- [ ] Actualizar política DMARC
- [ ] Auditar conteúdo de emails

### Ações Anuais
- [ ] Renovar certificados/chaves
- [ ] Revisar estratégia completa
- [ ] Avaliar novos providers SMTP
- [ ] Actualizar compliance legal

---

## Conclusão

Reputação de email é:

✅ **Construída gradualmente** (4+ semanas)  
✅ **Mantida com consistência** (diário)  
❌ **Destruída rapidamente** (1 dia de erros)  
❌ **Difícil de recuperar** (4-12 semanas)  

**Investimento**: Tempo e atenção  
**Retorno**: Alta deliverability para sempre  

---

**Próximo passo**: Ler [03-CONFIGURACAO-DNS.md](./03-CONFIGURACAO-DNS.md) para configurar autenticação.
