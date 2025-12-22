# Estratégia de Warm-up - Construção de Reputação

## Objetivo

Estabelecer e construir uma reputação sólida para o domínio de envio ao longo de 4 semanas, permitindo escalar a capacidade de envio de forma segura.

## Princípio Fundamental

**O warm-up simula comportamento humano gradual e consistente**, sinalizando aos ESPs (Email Service Providers) que você é um remetente legítimo.

## Cronograma de 4 Semanas

### Semana 1: Estabelecimento Inicial (350 emails)

**Volume Diário**: 50 emails/dia  
**Duração Total**: ~2.5 horas/dia (3 minutos entre emails)  
**Objetivo**: Criar baseline inicial de reputação

#### Ações Específicas:
- ✅ Configurar SPF, DKIM, DMARC
- ✅ Validar conexão SMTP
- ✅ Enviar primeiro batch de 50 emails
- ✅ Monitorizar métricas iniciais
- ✅ Verificar blacklist status

**Critérios de Sucesso para Avançar**:
- Bounce rate < 2%
- Nenhum spam complaint
- Emails chegando em inbox (não spam)

---

### Semana 2: Crescimento Controlado (1.050 emails)

**Volume Diário**: 150 emails/dia  
**Duração Total**: ~7.5 horas/dia  
**Objetivo**: Escalar gradualmente mantendo métricas saudáveis

#### Ações Específicas:
- ✅ Aumentar volume para 150/dia
- ✅ Monitorizar open rate (deve ser > 15%)
- ✅ Ajustar horários de envio se necessário
- ✅ Verificar feedback loops

**Critérios de Sucesso para Avançar**:
- Open rate > 15%
- Bounce rate < 2%
- Spam complaints < 0.1%
- Reputação estável

---

### Semana 3: Escalamento Confiante (2.800 emails)

**Volume Diário**: 400 emails/dia  
**Duração Total**: ~20 horas/dia  
**Objetivo**: Estabelecer padrão de alto volume com reputação sólida

#### Ações Específicas:
- ✅ Escalar para 400/dia com confiança
- ✅ Implementar templates otimizados (60-70% texto)
- ✅ Testar diferentes subject lines
- ✅ Monitorizar engagement detalhadamente

**Critérios de Sucesso para Avançar**:
- Open rate > 20%
- Delivery rate > 95%
- Reputação em Gmail/Outlook positiva

---

### Semana 4: Capacidade Plena (3.000+ emails)

**Volume Diário**: 600+ emails/dia  
**Duração Total**: ~30 horas/dia  
**Objetivo**: Operar em capacidade plena com reputação estabelecida

#### Ações Específicas:
- ✅ Completar envio da lista completa
- ✅ Manter consistência de horários
- ✅ Continuar monitorização ativa
- ✅ Documentar padrões de sucesso

**Métricas Finais Esperadas**:
- Open rate: 20-25%
- Delivery rate: 95-98%
- Bounce rate: < 2%
- Spam complaints: < 0.1%

---

## Regras de Ouro do Warm-up

### 1. Comece Devagar
- Primeiro dia: **50 emails no máximo**
- Nunca pule etapas

### 2. Aumente Gradualmente
- Incremento diário: 10-20 emails
- Apenas se métricas estiverem boas

### 3. Monitore Constantemente
- Verificar métricas 2x por dia
- Reagir imediatamente a problemas

### 4. Divida em Lotes
- 10-20 emails por hora
- Delay de 3 minutos entre emails

### 5. Mantenha Consistência
- Mesmos horários diariamente
- Preferencialmente horário de escritório (10h-18h PT)

---

## Sinais de Alerta

### 🚨 PARAR IMEDIATAMENTE se:
- Bounce rate > 5%
- Spam complaints > 0.3%
- Domínio entrar em blacklist
- Delivery rate < 85%

### ⚠️ REDUZIR VOLUME se:
- Open rate < 10%
- Bounce rate entre 2-5%
- Feedback negativo consistente

### ✅ CONTINUAR ESCALANDO se:
- Todas as métricas estão verdes
- Sem reclamações
- Engagement positivo

---

## Ferramentas de Monitorização Recomendadas

1. **Google Postmaster Tools** - Reputação em Gmail
2. **MXToolbox Blacklist Check** - Verificar blacklists
3. **Mail-Tester.com** - Score de spam antes de campanhas
4. **SendCraft Built-in Monitoring** - Métricas internas

---

## Implementação no SendCraft

O sistema já possui capacidades necessárias:
- ✅ `email_queue.py` - Sistema de filas
- ✅ `smtp_service.py` - Envio com delays configuráveis
- ✅ Logging completo de status
- ✅ Rate limiting por conta

**Próximo**: Implementar scheduler automático para warm-up gradual.

---

**Lembre-se**: Paciência durante o warm-up é investimento em reputação de longo prazo. Apressar o processo pode destruir meses de trabalho em dias.
