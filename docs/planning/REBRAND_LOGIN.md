# Plano de Rebrand — Página de Login

> **Objetivo**: transformar a página de login num layout profissional com identidade ABACO,
> alinhado ao design do interior do sistema.

---

## Diagnóstico atual

A página de login atual é funcional mas básica:
- Cartão branco centralizado com logo + formulário
- Sem identidade visual forte
- Sem ilustração ou elemento visual marcante
- Links "Esqueci minha senha" e "Criar conta" no rodapé

---

## Sprint Único — Redesign completo da tela de login

### Layout: Split screen

```
┌────────────────────┬──────────────────────┐
│                    │                      │
│   🔶 ABACO         │   Entrar no SGA      │
│                    │                      │
│   Transformando    │   [ email ]          │
│   vidas através    │   [ senha ]          │
│   da educação      │   [ ▢ Lembrar ]      │
│                    │                      │
│   [Ilustração ou   │   [   ENTRAR   ]     │
│    padrão visual]  │                      │
│                    │   Esqueci a senha    │
│                    │   Criar uma conta    │
│                    │                      │
└────────────────────┴──────────────────────┘
```

### Issues

- [ ] **1. Left panel (brand)** — fundo escuro com gradiente, logo ABACO grande, slogan, padrão sutil
- [ ] **2. Right panel (form)** — fundo claro, cartão de login limpo, campos com ícones, botão laranja ABACO
- [ ] **3. Animações** — fade-in suave ao carregar, transição no hover dos botões
- [ ] **4. Ícones nos campos** — ícone de email ✉ e cadeado 🔒 nos inputs
- [ ] **5. Checkbox "Lembrar-me"** — funcionalidade opcional de persistir sessão
- [ ] **6. Responsividade** — mobile: painéis empilhados verticalmente, brand no topo reduzido
- [ ] **7. Estado de erro** — animação de shake no card + mensagem de erro estilizada
- [ ] **8. Estado de loading** — botão com spinner integrado e texto "Entrando..."

### Cores

| Elemento | Cor | Hex |
|----------|-----|-----|
| Fundo brand panel | Gradiente escuro | `#1a1a2e` → `#0f172a` |
| Acento ABACO | Laranja | `#f2a93b` |
| Botão primário | Laranja ABACO | `#f2a93b` (hover: `#e09820`) |
| Texto brand | Branco | `#ffffff` |
| Link | Laranja | `#f2a93b` |
| Erro | Vermelho | `#d93025` |
