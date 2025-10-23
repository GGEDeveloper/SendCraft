# 🧪 PROMPT — Phase 14A (Domínios)

Copiar/colar no agente para implementar rotas, templates e validações.

---

Título: SendCraft Phase 14A — Domain Management (CRUD)

Contexto:
- Implementar UI e rotas para gerir Domínios de email no admin sem quebrar funcionalidades existentes.
- Reusar Bootstrap 5, toasts e padrões do projeto.

Tarefas:
1) Rotas Flask
- GET /domains — lista com paginação e search
- GET/POST /domains/new — criar
- GET/POST /domains/<id>/edit — editar
- POST /domains/<id>/toggle — ativar/desativar
- POST /domains/<id>/delete — apagar (bloquear se tiver contas ativas, ou soft delete)

2) Templates Jinja2
- templates/domains/list.html — tabela, search, ações
- templates/domains/form.html — formulário (nome, descrição, ativo)

3) Validações
- Nome de domínio válido (regex) e único
- Mensagens PT-PT; toasts sucesso/erro

4) Testes Manuais
- Criar 2 domínios válidos; tentar inválido
- Editar, toggle e delete protegido
- Screenshots + mini relatório

Critérios de aceitação:
- CRUD completo funcional
- Sem 500; UX consistente
- Nenhuma alteração em APIs v1; email client intacto
