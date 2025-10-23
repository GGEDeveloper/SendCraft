# 🧪 PROMPT — Phase 14C (API Access)

Copiar/colar no agente para implementar gestão de chaves e permissões de API por conta.

---

Título: SendCraft Phase 14C — API Access per Account

Contexto:
- Implementar gestão de acesso API por conta (enable/disable) e ciclo de vida de chaves (gerar, rotacionar, revogar) sem expor segredos.

Tarefas:
1) Modelo/DB
- EmailAccount: api_enabled (bool), api_key_hash (str), api_created_at, api_last_used_at
- Utilitário: generate_api_key(), verify_api_key(), rotate_api_key()

2) Rotas Admin
- GET /accounts/<id>/api — gestão API de uma conta
- POST /accounts/<id>/api/enable — toggle enable/disable
- POST /accounts/<id>/api/generate — gerar/rotacionar chave (mostrar **uma vez**)
- POST /accounts/<id>/api/revoke — revogar chave (inutilizar)

3) Integração External API
- Middleware: Authorization Bearer <key> → mapear para conta com api_enabled True e verify_api_key
- Rate limit por conta (usar existente se disponível)

4) Templates
- templates/accounts/api_access.html — UI de gestão (botões, key mascarada, copy to clipboard, datas)

5) Testes Manuais
- Ativar API; gerar chave; testar com curl Authorization: Bearer <key>
- Rotacionar chave; confirmar antiga inválida
- Revogar; confirmar 401

Critérios de aceitação:
- Chaves nunca armazenadas em plain text
- UI mostra chave apenas na geração e sempre mascarada depois
- Endpoints rejeitam conta sem permissão ou chave inválida
- Logs sem exposição de segredos
