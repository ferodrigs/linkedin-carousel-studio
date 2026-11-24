# Visão de Produto V2 — LinkedIn Carousel Studio (Aplicação Completa)

**Objetivo:** Transformar o `linkedin-carousel-studio` em uma aplicação local-first completa de criação semanal de carrosséis e conteúdo editorial para LinkedIn, reaproveitando os módulos visuais e de estúdio já validados no `apps/content-lab` — **100% desacoplada de recursos corporativos** (zero GCP, Firestore, BigQuery ou Auth corporativo).

---

## 1. O Que Reaproveitamos do `apps/content-lab`

| Módulo do `content-lab` | Como entra no Carousel Studio V2 | O que removemos |
|---|---|---|
| **Shell Cyber Dark (React 19 + Tailwind)** | Casca da aplicação (`#09090B`, `#111114`, Radix UI + Sonner Toasts) | Login SSO/OTP corporativo |
| **Estúdio Reversível em 3 Etapas** | Fluxo `Roteiro (.md) ↔ Estúdio Visual ↔ Publicação (PDF/PPTX)` com `slide_uid` | Conexões BigQuery / `safra` mensal |
| **1-Clique Global vs Neste Slide** | Aplicar paleta, gradiente ou fonte apenas no slide atual ou no carrossel todo | Regras de clientes/agência |
| **Catálogo Visual & Construtores** | Galeria de **Paletas**, **Fontes** (`display`/`body`/`mono`), **1.800 Ícones SVG (Neat Icons)** e **Construtor de Gradientes/Fundos** | Persistência em Firestore/GCS (passa para JSON/FS local) |
| **Motor `html_to_pptx` + Playwright** | Exportação 1:1 `4:5` (`1080×1350`), `1:1` (`1080×1080`) e `16:9` (`1920×1080`) | Restrições airgapped de Cloud Run |

---

## 2. Pilares da Experiência V2 (Foco em Velocidade Semanal)

### A. Editor de Texto Nativo no Palco
- **Edição Direta (Inline):** Clicar e digitar direto no slide, com barra flutuante contextual (**Negrito**, **Cor de Destaque**, **Tamanho `px`**, **Line-Height**, **Alinhamento**).
- **Reversibilidade Roteiro ↔ Visual:** Editar o texto no painel de Roteiro (`.md`) atualiza o slide sem perder os ajustes visuais de fonte, cor ou layout.
- **Undo / Redo (`Ctrl+Z` / `Ctrl+Y`):** Histórico em memória por sessão.

### B. Troca de Template & Layouts por Slide (Sem Perder Conteúdo)
Cada slide possui um **Layout Semântico** intercambiável em 1 clique:
1. `cover-orbital` — Capa com título serif + diagrama orbital + índice inferior.
2. `manifesto-gradient` — Card gradiente cobalt/lavanda com citação âncora.
3. `bento-stack-3` — 3 cards horizontais empilhados (passado / diagnóstico / passos).
4. `big-number-split` — 2 colunas com números gigantes + card takeaway escuro.
5. `case-diagram` — Texto + diagrama vetorial (curadoria / fluxo) + citação lateral.
6. `bento-grid-2x2` — Matriz 2×2 comparativa (*De → Para*).
7. `terminal-guardrail` — Card branco + bloco terminal com barra de espectro.
8. `cta-debate` — Provocação final + caixa de chamada para comentários.

### C. Sistema de Cores, Gradientes e Fundos
- **Presets de Tema por Slide:** `Pedra Claro (#F2F1ED)`, `Preto Carbono (#18181A)`, `Azul Cobalto (#1D39FF)` ou customizado.
- **Editor de Gradientes & Texturas:** Controle visual de ângulo, 2–3 stops de cor (ex: Cobalt → Lavanda → Carbono), toggle de **Dot-Grid** e **Halftone/Dithering**.
- **Escopo Inteligente:** Botão `Aplicar neste slide` vs `Aplicar em todos os slides`.

### D. Exportação com Progresso Real & Biblioteca de Formatos
- **Loading & Feedback:** Barra de progresso por etapa (*Salvando HTML → Renderizando PDF → Medindo DOM → Montando PPTX*).
- **Pacote de Publicação:** Botão único **"Exportar Kit LinkedIn"** que entrega `PDF` + `PPTX` + `Copy do Post` pronta para colar.

---

## 3. Roadmap de Execução (3 Fases)

- **Fase 1 (Fundação React + FastAPI Local):** Migrar a casca Cyber Dark do `content-lab` para `frontend/` + backend FastAPI local (`backend/`) lendo/salvando direto em `carousels/<slug>/`.
- **Fase 2 (Editor Nativo + Templates + Cores/Gradientes):** Implementar troca de layout por slide, editor inline com barra flutuante, seletor de gradientes/dot-grid e `Undo/Redo`.
- **Fase 3 (Biblioteca de Referências & Novo Carrossel):** Catálogo de ícones SVG/diagramas reutilizáveis e gerador assistido de roteiro → carrossel a partir de notas de estudo (`.md`).
