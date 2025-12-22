# Estratégia de Envio Gradual - SendCraft

## Visão Geral

Este documento define a estratégia completa para envio de emails em listas usando **uma única conta SMTP**, com foco em **construção de reputação** e evitar blacklists.

## Contexto

- **Objetivo**: Enviar emails em massa de forma segura e escalável
- **Conta única**: Todo o envio será feito através de uma única conta de email
- **Desafio principal**: Construir e manter boa reputação junto aos provedores de email (Gmail, Outlook, etc.) e centros de detecção de spam

## Problema a Resolver

**Enviar milhares de emails de uma vez destruirá a reputação do domínio** e resultará em:
- Emails indo direto para spam (70-90% de taxa de spam)
- Domínio entrar em blacklists
- Taxa de entrega de apenas 40-50%
- Possível bloqueio permanente da conta SMTP

## Solução: Warm-up Gradual de 4 Semanas

### Princípio Fundamental

**O warm-up é obrigatório e não deve ser pulado.** Provedores de email monitorizam padrões de envio e penalizam aumentos repentinos de volume.

### Cronograma Recomendado

| Semana | Emails/Dia | Total Semana | Duração Envio/Dia | Ações Principais |
|--------|------------|--------------|-------------------|------------------|
| 1 | 50 | 350 | 2.5h | Setup técnico, primeiros testes, monitorização inicial |
| 2 | 150 | 1.050 | 7.5h | Validar métricas, ajustar se necessário |
| 3 | 400 | 2.800 | 20h | Escalar com confiança, validação contínua |
| 4 | 600 | 3.000+ | 30h | Completar envio da lista completa |

**Delay entre emails**: 3 minutos (simula comportamento humano)

### Regras de Ouro do Warm-up

1. **Começar devagar**: 50 emails no primeiro dia, não mais
2. **Aumentar gradualmente**: 10-20% por dia se métricas estiverem boas
3. **Monitorizar constantemente**: Acompanhar bounce rate, open rate, spam complaints
4. **Dividir em lotes**: 10-20 emails por hora máximo
5. **Manter consistência**: Enviar nos mesmos horários todos os dias
6. **Horário comercial**: Enviar entre 9h-18h (horário de escritório PT)

## Métricas Críticas a Monitorizar

### 1. Taxa de Abertura (Open Rate)
- **Ideal**: ≥ 20%
- **Alerta**: < 10% → Revisar assunto e conteúdo

### 2. Taxa de Bounce
- **Aceitável**: ≤ 2%
- **CRÍTICO**: ≥ 5% → **PARAR IMEDIATAMENTE** e limpar lista

### 3. Taxa de Spam Complaints
- **Máximo**: ≤ 0.1% (Google exige < 0.3%)
- **Alerta**: Qualquer aumento → Reduzir volume em 30%

### 4. Blacklist Status
- **Verificar diariamente**: Usar [MXToolbox](https://mxtoolbox.com/blacklists.aspx)
- **Ação imediata**: Se entrar em blacklist, seguir processo de remoção

### 5. Taxa de Entrega
- **Esperado após warm-up**: 95-98%
- **Durante warm-up**: Pode variar, monitorizar tendência

## Pré-requisitos Técnicos Obrigatórios

### Configuração DNS (CRÍTICO)

**Sem estas configurações, 100% dos emails vão para spam:**

#### 1. SPF (Sender Policy Framework)
Registo TXT no DNS:
```
v=spf1 include:spf.antispamcloud.com a mx ~all
```

#### 2. DKIM (DomainKeys Identified Mail)
- Gerar chave DKIM no provider SMTP (cPanel ou SpamExperts)
- Adicionar registo DKIM ao DNS
- Valida autenticidade digital dos emails

#### 3. DMARC (Domain-based Message Authentication)
Registo TXT no DNS:
```
v=DMARC1; p=none; rua=mailto:postmaster@[SEU-DOMINIO]
```

**Política recomendada**:
- Iniciar com `p=none` (monitorização)
- Após validação, evoluir para `p=quarantine`
- Produção: `p=reject`

### Validação DNS

Ferramentas para validar configuração:
- [MXToolbox SuperTool](https://mxtoolbox.com/SuperTool.aspx)
- [DMARC Analyzer](https://dmarcreport.com/)
- [Mail-Tester](https://www.mail-tester.com/)

## Arquitetura do Sistema de Envio Gradual

### Componentes Necessários

```
┌─────────────────────────────────────────┐
│   Sistema de Envio Gradual SendCraft   │
├─────────────────────────────────────────┤
│                                         │
│  1. Queue System (Fila de Envio)       │
│     - Lista segmentada em lotes        │
│     - Controlo de velocidade           │
│     - Retry automático                 │
│                                         │
│  2. Throttling Engine                   │
│     - Delay 3 min entre emails         │
│     - Limite diário dinâmico           │
│     - Rate limiting inteligente        │
│                                         │
│  3. Monitoring System                   │
│     - Bounce tracking                  │
│     - Open rate tracking               │
│     - Spam complaint detection         │
│     - Blacklist monitoring             │
│                                         │
│  4. Template Engine                     │
│     - Templates otimizados             │
│     - Variáveis personalizadas         │
│     - HTML sanitizado                  │
│                                         │
│  5. Alerting System                     │
│     - Alertas automáticos              │
│     - Pausa automática em caso crítico │
│                                         │
└─────────────────────────────────────────┘
```

## Próximos Passos

Ver documentos específicos:

1. **[01-CONFIGURACAO-DNS.md](./01-CONFIGURACAO-DNS.md)** - Setup DNS completo
2. **[02-TEMPLATE-OTIMIZADO.md](./02-TEMPLATE-OTIMIZADO.md)** - Templates anti-spam
3. **[03-SISTEMA-QUEUE.md](./03-SISTEMA-QUEUE.md)** - Implementação da fila
4. **[04-MONITORAMENTO.md](./04-MONITORAMENTO.md)** - Sistema de monitorização
5. **[05-PLANO-CONTINGENCIA.md](./05-PLANO-CONTINGENCIA.md)** - Ações de emergência

## Taxa de Sucesso Esperada

Com implementação correta:

- **Taxa de Entrega**: 95-98%
- **Taxa de Abertura**: 15-25%
- **Taxa de Bounce**: ≤ 2%
- **Taxa de Spam Complaints**: ≤ 0.1%
- **Reputação do Domínio**: Excelente após 4 semanas

---

**Nota Importante**: Este processo leva tempo mas é essencial. Pular o warm-up significa comprometer permanentemente a reputação do domínio.
