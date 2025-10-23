# 📂 Phase 14A — Gestão de Domínios (CRUD)

## Objetivo
Implementar CRUD de domínios de email com validações e UX consistente.

## Requisitos Funcionais
- Listar domínios com paginação e busca por nome
- Criar/editar domínio: nome (obrigatório), descrição (opcional), ativo (bool)
- Toggle ativo/inativo
- Remoção segura (bloquear se tiver contas ativas, ou soft delete)

## Rotas
- GET /domains — lista
- GET/POST /domains/new — criar
- GET/POST /domains/{id}/edit — editar
- POST /domains/{id}/toggle — alternar ativo
- POST /domains/{id}/delete — remover (seguro)

## Validações
- Nome válido de domínio (regex)
- Único por sistema
- Não permitir delete se tiver contas ativas (ou exigir confirmação forte)

## Templates
- templates/domains/list.html — tabela, search, paginação, ações
- templates/domains/form.html — formulário Bootstrap 5, validações

## Notas Técnicas
- Reusar Domain model
- Adicionar search e ordenação por nome
- Toasts de sucesso/erro, mensagens PT-PT

## Testes Manuais
- Criar 2 domínios válidos
- Tentar criar inválido (erro)
- Editar, toggle e delete protegido
- Screenshots + mini relatório
