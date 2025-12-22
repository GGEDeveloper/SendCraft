# Campanha de Envio em Listas - SendCraft

## Visão Geral

Este documento descreve a estratégia completa para envio de emails em listas através do SendCraft, com foco especial em **construção de reputação** e **warm-up gradual** para maximizar deliverability.

## Contexto do Projeto

- **Sistema**: SendCraft Email Manager
- **Conta**: Uma única conta de email
- **Objetivo**: Construir reputação sólida para escalar capacidade de envio
- **Abordagem**: Warm-up gradual de 4 semanas

## Documentação Disponível

### 📋 Estratégia e Planeamento
- [00-RESUMO-EXECUTIVO.md](./00-RESUMO-EXECUTIVO.md) - Sumário da estratégia
- [01-ESTRATEGIA-WARMING.md](./01-ESTRATEGIA-WARMING.md) - Plano de warm-up 4 semanas
- [02-CONSTRUCAO-REPUTACAO.md](./02-CONSTRUCAO-REPUTACAO.md) - Como construir boa reputação

### 🔧 Implementação Técnica
- [03-CONFIGURACAO-DNS.md](./03-CONFIGURACAO-DNS.md) - SPF, DKIM, DMARC
- [04-TEMPLATES-EMAIL.md](./04-TEMPLATES-EMAIL.md) - Templates otimizados
- [05-SCRIPTS-AUTOMACAO.md](./05-SCRIPTS-AUTOMACAO.md) - Scripts Python

### 📊 Monitorização e Controlo
- [06-MONITORAMENTO.md](./06-MONITORAMENTO.md) - Métricas críticas
- [07-PLANO-CONTINGENCIA.md](./07-PLANO-CONTINGENCIA.md) - Ações emergenciais

## Quick Start

### 1. Configuração DNS (Crítico)
```bash
# Ver instruções detalhadas em 03-CONFIGURACAO-DNS.md
# Configurar SPF, DKIM e DMARC antes de qualquer envio
```

### 2. Warm-up Gradual
```
Semana 1: 50 emails/dia  (Total: 350)
Semana 2: 150 emails/dia (Total: 1.050)
Semana 3: 400 emails/dia (Total: 2.800)
Semana 4: 600 emails/dia (Total: 3.000+)
```

### 3. Monitorização Diária
- Taxa de bounce < 2%
- Taxa de abertura > 20%
- Spam complaints < 0.1%
- Verificar blacklists diariamente

## Princípios Fundamentais

### 🎯 Construção de Reputação

1. **Começar Devagar**: 50 emails no primeiro dia, não mais
2. **Aumentar Gradualmente**: 10-20% por dia se métricas estiverem boas
3. **Consistência**: Mesmos horários de envio diariamente
4. **Qualidade**: Templates otimizados (60-70% texto, 30-40% imagens)
5. **Autenticação**: SPF, DKIM e DMARC configurados corretamente

### ⚠️ Sinais de Alerta

**PARAR IMEDIATAMENTE se:**
- Bounce rate > 5%
- Entrar em qualquer blacklist
- Spam complaints > 0.5%
- Taxa de abertura < 10%

## Resultados Esperados

Com warm-up correto:
- **Taxa de Entrega**: 95-98%
- **Taxa de Abertura**: 20-25%
- **Taxa de Bounce**: < 2%
- **Spam Complaints**: < 0.1%

Sem warm-up (envio direto):
- **Taxa de Entrega**: 40-50%
- **Risco de Blacklist**: 80%
- **Reputação**: Destruída permanentemente

## Próximos Passos

1. Ler [00-RESUMO-EXECUTIVO.md](./00-RESUMO-EXECUTIVO.md)
2. Configurar DNS seguindo [03-CONFIGURACAO-DNS.md](./03-CONFIGURACAO-DNS.md)
3. Implementar warm-up seguindo [01-ESTRATEGIA-WARMING.md](./01-ESTRATEGIA-WARMING.md)
4. Monitorizar métricas via [06-MONITORAMENTO.md](./06-MONITORAMENTO.md)

## Suporte

Para questões técnicas, consultar a documentação completa em cada ficheiro específico.
