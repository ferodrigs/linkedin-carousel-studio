# LinkedIn Carousel Studio

Estúdio local para criação, ajuste visual rápido e exportação 1:1 (**HTML → PDF vetorial + PPTX editável**) de carrosséis técnicos para LinkedIn no padrão **Tech Minimalista Editorial** (`Pedra Claro #F2F1ED`, `Preto Carbono #18181A`, `Azul Cobalto #1D39FF`).

---

## Por que este projeto existe

Carrosséis de LinkedIn exigem leitura **mobile-first** (`1080 × 1350 px`, proporção `4:5`): textos abaixo de `24px` ficam ilegíveis no feed do celular, e espaços vazios mal planejados reduzem a retenção.

Este estúdio resolve três gargalos de fluxo:
1. **Edição visual instantânea no navegador:** clique em qualquer título, card ou parágrafo para ajustar `font-size`, `line-height`, `padding` e texto com preview em escala desktop e **simulação mobile (`360px`)**.
2. **Auditoria de legibilidade em tempo real:** contagem de palavras e verificação automática do menor tamanho de fonte por slide.
3. **Exportação 100% fiel ao HTML:** gera **PDF multi-página** pronto para o LinkedIn e **PPTX nativo editável** com exatamente as mesmas dimensões, fontes e posicionamento do DOM renderizado no Chromium.

---

## Estrutura do Repositório

- `studio/` — Servidor Python local (`server.py`) e interface visual (`index.html`) para ajustes rápidos.
- `engine/` — Motor unificado de exportação (`export_all.py` + `html_to_pptx/`) com suporte a `4:5` (`1080×1350`), `1:1` (`1080×1080`) e `16:9` (`1920×1080`).
- `design-system/` — Tokens CSS canônicos (`tokens.css`) com paleta, tipografia editorial/mono, Bento Grids e blocos de terminal.
- `docs/` — Guia de formatos, escala tipográfica mobile-first e frameworks de alta retenção no LinkedIn (`LINKEDIN_FORMATS_GUIDE.md`).
- `carousels/` — Projetos semanais de carrosséis (HTML, roteiro/copy, PDF e PPTX).

---

## Como Usar

### 1. Iniciar o Studio Visual

```powershell
python studio/server.py
```

Abra `http://127.0.0.1:4100`, selecione o carrossel, ajuste fontes/espaçamentos clicando nos elementos e exporte **PDF** ou **PPTX** em um clique.

### 2. Exportar via Linha de Comando (CLI)

```powershell
python engine/export_all.py carousels/o-fim-da-linha-reta/index.html --format 4:5 --previews
```

---

## Licença

MIT — [Fernando Rodrigues](https://github.com/ferodrigs)
