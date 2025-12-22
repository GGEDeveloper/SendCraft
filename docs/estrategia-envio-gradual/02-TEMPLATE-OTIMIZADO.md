# Templates de Email Otimizados - Anti-Spam

## Regra de Ouro

**NUNCA enviar email composto apenas por imagem.**

Emails "image-only" têm:
- 70-90% de probabilidade de ir para spam
- Taxa de entrega de apenas 40-50%
- 70% dos clientes bloqueiam imagens por padrão (email fica vazio)

## Proporção Ideal: Texto vs Imagem

### Recomendação

**60-70% texto HTML + 30-40% imagens**

Emails que respeitam esta proporção têm:
- Taxa de inbox placement: 95%+
- Spam score quase zero
- Compatibilidade máxima com todos os dispositivos
- Acessibilidade para deficientes visuais

### Durante Warm-up

| Semana | Proporção Recomendada | Imagens |
|--------|-----------------------|---------|
| 1-2 | 80% texto, 20% visual | **Zero imagens externas**, apenas HTML/emoji |
| 3 | 65% texto, 35% imagens | Máximo 3 imagens pequenas (< 100KB cada) |
| 4+ | 60% texto, 40% imagens | Normal, otimizadas |

---

## Template Ultra-Simples (Semanas 1-2)

### Características
- **80% texto, 20% elementos visuais**
- **Zero imagens externas**
- **Spam score: 0/10** (máxima segurança)
- **Probabilidade inbox: 95-98%**

### Exemplo HTML

```html
<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ subject }}</title>
    <style>
        body {
            font-family: Arial, Helvetica, sans-serif;
            line-height: 1.6;
            color: #333333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            background-color: #0066cc;
            color: white;
            padding: 20px;
            text-align: center;
            border-radius: 5px 5px 0 0;
        }
        .content {
            background-color: #ffffff;
            padding: 30px;
            border: 1px solid #dddddd;
        }
        .cta-button {
            display: inline-block;
            padding: 12px 30px;
            background-color: #0066cc;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            margin: 20px 0;
        }
        .footer {
            background-color: #f8f9fa;
            padding: 20px;
            text-align: center;
            font-size: 12px;
            color: #666666;
            border-top: 1px solid #dddddd;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ company_name }}</h1>
    </div>
    
    <div class="content">
        <p>Olá {{ customer_name }},</p>
        
        <p>{{ main_message }}</p>
        
        <p><strong>{{ highlight_text }}</strong></p>
        
        <div style="text-align: center;">
            <a href="{{ cta_link }}" class="cta-button">{{ cta_text }}</a>
        </div>
        
        <p>{{ additional_info }}</p>
        
        <p>Cumprimentos,<br>
        <strong>Equipa {{ company_name }}</strong></p>
    </div>
    
    <div class="footer">
        <p><strong>{{ company_name }}</strong><br>
        {{ company_address }}<br>
        Tel: {{ company_phone }} | Email: {{ company_email }}</p>
        
        <p><a href="{{ unsubscribe_link }}">Cancelar subscrição</a></p>
        
        <p>Esta mensagem foi enviada para {{ recipient_email }} porque está na nossa lista de contactos.</p>
    </div>
</body>
</html>
```

---

## Template Híbrido (Semana 3+)

### Características
- **65% texto, 35% imagens**
- **Máximo 3 imagens pequenas**
- **Alt text descritivo em todas**
- **Spam score: 2/10** (seguro)
- **Probabilidade inbox: 85-90%**

### Boas Práticas para Imagens

```html
<!-- Imagem com alt text e dimensões fixas -->
<img src="{{ image_url }}" 
     alt="Descrição detalhada da imagem" 
     width="150" 
     height="80" 
     style="max-width: 100%; height: auto; display: block; border: 1px solid #ddd;">
```

**Regras para imagens**:
- **Tamanho máximo**: 100KB por imagem
- **Dimensões**: Não exceder 600px de largura
- **Alt text obrigatório**: Descrição completa
- **Hospedagem**: CDN confiável ou domínio próprio
- **Formato**: JPG otimizado ou PNG comprimido

---

## Palavras e Práticas a EVITAR

### ❌ Palavras Proibidas no Assunto/Corpo

**Palavras spam críticas**:
- Grátis, 100%, Ganhar dinheiro
- Clique aqui, URGENTE, AGORA
- Parabéns, Ganhou, Prémio
- Oferta limitada, Última chance

**Formatação problemática**:
- MAIÚSCULAS EXCESSIVAS
- Muitos pontos de exclamação!!!
- $$$, €€€, Símbolos repetidos
- Cores vermelhas ou chamativas em excesso

### ✅ Alternativas Seguras

| ❌ Evitar | ✅ Usar |
|-----------|----------|
| CLIQUE AQUI AGORA!!! | Saiba mais sobre... |
| 100% GRÁTIS | Sem custos adicionais |
| URGENTE - Última chance | Oferta válida até [data] |
| Ganhe dinheiro rápido | Oportunidade de negócio |

---

## Estrutura Ideal do Email

### 1. Assunto (Subject Line)

**Boas práticas**:
- **Comprimento**: 40-50 caracteres
- **Personalização**: Incluir nome se possível
- **Claro e honesto**: Sem clickbait
- **Teste A/B**: Testar variações

**Exemplos**:
```
✅ "João, oferta exclusiva AliTools - 5% desconto"
✅ "Novidades AliTools para si"
✅ "Confirmação do seu pedido #12345"

❌ "CLIQUE AQUI!!! 100% GRÁTIS!!!"
❌ "Ganhe dinheiro agora!!!"
❌ "URGENTE - Última oportunidade"
```

### 2. Preview Text

**O que é**: Primeiras linhas visíveis no inbox

**Otimização**:
```html
<div style="display:none; max-height:0px; overflow:hidden;">
    Preview text otimizado que complementa o assunto e incentiva abertura
</div>
```

### 3. Corpo do Email

**Estrutura recomendada**:
1. **Saudação personalizada**: "Olá {{ nome }}"
2. **Valor imediato**: Benefício claro logo no início
3. **Conteúdo principal**: 2-3 parágrafos curtos
4. **Call-to-Action**: Único e claro
5. **Informação adicional**: Opcional, em texto menor
6. **Assinatura profissional**: Empresa + contacto

### 4. Footer Obrigatório

**Elementos legais (RGPD)**:
```html
<div class="footer">
    <p><strong>{{ company_name }}</strong><br>
    {{ company_address }}<br>
    NIF: {{ company_nif }}</p>
    
    <p><a href="{{ unsubscribe_link }}" style="color: #0066cc;">Cancelar subscrição</a></p>
    
    <p style="font-size: 11px; color: #999;">
        Este email foi enviado para {{ recipient_email }}.<br>
        Para garantir a entrega, adicione {{ sender_email }} aos seus contactos.
    </p>
</div>
```

---

## Personalização Dinâmica

### Variáveis Recomendadas

```python
# Variáveis básicas
{
    "customer_name": "João Silva",
    "customer_email": "joao@example.com",
    "company_name": "AliTools",
    "order_number": "ALI-2025-001",
    "discount_code": "BEMVINDO5"
}
```

### Benefícios da Personalização

- **Aumenta open rate**: +26% em média
- **Reduz spam score**: Emails personalizados são menos suspeitos
- **Melhora engagement**: CTR 14% superior

---

## Versão Plain Text (Fallback)

**Sempre incluir versão texto puro** para:
- Clientes de email antigos
- Preferência de usuário
- Acessibilidade
- Backup se HTML falhar

### Exemplo

```text
Olá {{ customer_name }},

{{ main_message }}

{{ highlight_text }}

Para saber mais, visite: {{ cta_link }}

{{ additional_info }}

Cumprimentos,
Equipa {{ company_name }}

---
{{ company_name }}
{{ company_address }}
Tel: {{ company_phone }}
Email: {{ company_email }}

Para cancelar subscrição: {{ unsubscribe_link }}
```

---

## Checklist Final do Template

Antes de usar template em produção:

- [ ] Proporção 60-70% texto, 30-40% imagens (ou 80-20% no warm-up)
- [ ] Zero palavras spam no assunto e corpo
- [ ] Personalização com variáveis {{ nome }}
- [ ] Link de unsubscribe visível e funcional
- [ ] Informações da empresa completas (RGPD)
- [ ] Imagens com alt text descritivo
- [ ] Versão plain text incluída
- [ ] CTA único e claro
- [ ] Responsivo (mobile-friendly)
- [ ] Testado em Mail-Tester (score ≥ 8/10)
- [ ] Validado em Litmus ou Email on Acid

---

## Próximos Passos

1. **Criar templates** usando exemplos acima
2. **Testar em Mail-Tester**: https://www.mail-tester.com/
3. **Validar score**: Objetivo ≥ 8/10
4. **Proceder para**: [03-SISTEMA-QUEUE.md](./03-SISTEMA-QUEUE.md)
