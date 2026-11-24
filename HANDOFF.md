# Session Handoff & Memory — LinkedIn Carousel Studio

**Última Atualização:** 2026-11-24  
**Repositório Canônico:** `https://github.com/ferodrigs/linkedin-carousel-studio`  
**Estado Atual:** OPERACIONAL

---

## 1. O Que Foi Construído
- Motor `engine/export_all.py` + `engine/html_to_pptx/` parametrizado para `4:5` (`1080×1350`), `1:1` (`1080×1080`) e `16:9` (`1920×1080`), gerando PDF vetorial e PPTX editável 100% fiéis ao HTML.
- Interface interativa `studio/server.py` + `studio/index.html` (`http://127.0.0.1:4100`) para ajuste rápido de `font-size`, `line-height`, `padding`, conteúdo de texto e simulação mobile (`360px`).
- Design System codificado em `design-system/tokens.css` (Pedra Claro `#F2F1ED`, Preto Carbono `#18181A`, Azul Cobalto `#1D39FF`, escala mobile-first `>= 24px`).
- Guia de formatos e retenção no LinkedIn em `docs/LINKEDIN_FORMATS_GUIDE.md`.
- Carrossel da semana (`carousels/o-fim-da-linha-reta/`) reconstruído em 4:5 com alta legibilidade e aproveitamento de espaço.

## 2. Comandos Canônicos
- **Abrir Studio Visual:** `python studio/server.py`
- **Exportar PDF + PPTX + Previews:** `python engine/export_all.py carousels/<slug>/index.html --format 4:5 --previews`
