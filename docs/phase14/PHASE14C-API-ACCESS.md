# 🔐 Phase 14C — Gestão de Acesso à API (por Conta)

## Objetivo
Permitir/impedir uso de API por conta e gerir chaves (gerar/rotacionar/revogar) de forma segura.

## Requisitos Funcionais
- Ativar/Desativar acesso API por conta
- Gerar chave (exibir apenas uma vez), copiar para clipboard
- Rotacionar chave (invalida anterior), revogar chave
- Mostrar apenas hash mascarado e metadados (criado, último uso)

## Alterações de Modelo
- EmailAccount: api_enabled (bool), api_key_hash (str), api_created_at, api_last_used_at
- Utilitário: generate_api_key(), verify_api_key(key, hash), rotate_api_key()

## Rotas Admin
- GET /accounts/{id}/api — gestão API da conta
- POST /accounts/{id}/api/enable — toggle
- POST /accounts/{id}/api/generate — gerar/rotacionar
- POST /accounts/{id}/api/revoke — revogar

## Integração com External API
- Middleware: mapear Bearer <key> → conta com api_enabled True e verify_api_key
- Rate limit por conta (usar existente se aplicável)

## Templates
- templates/accounts/api_access.html — botões e estados, máscara de chave

## Testes Manuais
- Ativar API numa conta
- Gerar chave e testar endpoint com curl (Authorization: Bearer <key>)
- Revogar chave e confirmar 401
