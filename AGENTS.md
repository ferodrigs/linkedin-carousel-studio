# LinkedIn Carousel Studio — Ficha Técnica Local

> **Herança Global:** Segue 100% a Constituição em [`../../AGENTS.md`](../../AGENTS.md).
> **Repositório Canônico:** `https://github.com/ferodrigs/linkedin-carousel-studio.git`

## 1. Arquitetura & Fluxo
- **Palco Padrão:** `1080 × 1350 px` (`4:5` LinkedIn Portrait), com suporte a `1:1` (`1080 × 1080`) e `16:9` (`1920 × 1080`).
- **Studio Interativo:** `python studio/server.py` (`http://127.0.0.1:4100`) — ajuste visual de fontes, espaçamentos, textos e simulação mobile `360px`.
- **Motor 1:1 HTML → PDF + PPTX:** `python engine/export_all.py carousels/<slug>/index.html --format 4:5`
