# ⚙️ Phase 14 — Admin de Configurações (Local Dev)

## Objetivo
Criar áreas administrativas internas para configuração do sistema, mantendo apenas ambiente local de desenvolvimento.

### Escopo da Phase 14
- 14A: Gestão de Domínios (CRUD, validações)
- 14B: Gestão de Contas de Email (CRUD, encriptação, teste IMAP/SMTP)
- 14C: Gestão de Acesso à API por conta (enable/disable, geração/rotação de chaves)

## Princípios
- Não quebrar funcionalidades do email client nem API v1
- Reusar design/UX existente (Bootstrap 5 + toasts)
- Segurança mínima: mascarar dados sensíveis; nunca logar segredos

## Sequência
1) 14A — Domínios (base de dados coerente)
2) 14B — Contas (herdam do domínio)
3) 14C — Acesso API (fecha integração futura)

## Entregáveis
- Documentação técnica por subfase
- Prompts de execução por subfase (agent)
- Testes manuais de validação
