#!/usr/bin/env python3
"""
export_all.py — Motor unificado de exportação HTML -> PDF + PPTX Editável + PNG Previews.

Suporta formatos de Carrossel LinkedIn (4:5 = 1080x1350, 1:1 = 1080x1080) e Deck (16:9 = 1920x1080)
com fidelidade 1:1 ao HTML renderizado no Chromium.

Uso:
  python engine/export_all.py carousels/o-fim-da-linha-reta/index.html
  python engine/export_all.py carousels/o-fim-da-linha-reta/index.html --format 4:5 --previews
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
import time
from pathlib import Path

ENGINE_DIR = Path(__file__).resolve().parent
H2P_DIR = ENGINE_DIR / "html_to_pptx"
sys.path.insert(0, str(H2P_DIR))

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

FORMAT_PRESETS = {
    "4:5": (1080, 1350),
    "1:1": (1080, 1080),
    "16:9": (1920, 1080),
}


def detect_stage_dimensions(page) -> tuple[int, int]:
    """Detecta dimensões da primeira .slide/[data-pptx-slide] no DOM."""
    dims = page.evaluate("""() => {
        const el = document.querySelector('[data-pptx-slide], .slide');
        if (!el) return null;
        const r = el.getBoundingClientRect();
        return { width: Math.round(r.width), height: Math.round(r.height) };
    }""")
    if dims and dims.get("width", 0) >= 300 and dims.get("height", 0) >= 300:
        return int(dims["width"]), int(dims["height"])
    return 1080, 1350


def export_pdf(page, out_pdf: Path, width_px: int, height_px: int) -> None:
    """Exporta PDF vetorial fiel 1:1 ao HTML, 1 slide por página."""
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    # Injeta CSS @page exato para impressão sem margens e 1 slide por página
    page.evaluate(f"""() => {{
        let style = document.getElementById('__carousel_pdf_print_css');
        if (!style) {{
            style = document.createElement('style');
            style.id = '__carousel_pdf_print_css';
            document.head.appendChild(style);
        }}
        style.textContent = `
            @page {{
                size: {width_px}px {height_px}px;
                margin: 0;
            }}
            @media print {{
                html, body {{
                    margin: 0 !important;
                    padding: 0 !important;
                    background: transparent !important;
                    -webkit-print-color-adjust: exact !important;
                    print-color-adjust: exact !important;
                }}
                .studio-toolbar, .no-print {{
                    display: none !important;
                }}
                .carousel-stage, .slides-container, main {{
                    display: block !important;
                    padding: 0 !important;
                    margin: 0 !important;
                    gap: 0 !important;
                    background: transparent !important;
                }}
                .slide, [data-pptx-slide] {{
                    width: {width_px}px !important;
                    height: {height_px}px !important;
                    margin: 0 !important;
                    box-shadow: none !important;
                    border-radius: 0 !important;
                    page-break-after: always !important;
                    break-after: page !important;
                    overflow: hidden !important;
                }}
                .slide:last-child, [data-pptx-slide]:last-child {{
                    page-break-after: auto !important;
                    break-after: auto !important;
                }}
            }}
        `;
    }}""")
    page.pdf(
        path=str(out_pdf),
        width=f"{width_px}px",
        height=f"{height_px}px",
        print_background=True,
        margin={"top": "0px", "right": "0px", "bottom": "0px", "left": "0px"},
        prefer_css_page_size=True,
    )
    print(f"[export-pdf] Salvo: {out_pdf} ({out_pdf.stat().st_size:,} B)")


def export_previews(page, previews_dir: Path, width_px: int, height_px: int) -> list[Path]:
    """Captura PNG de cada slide para inspeção visual rápida."""
    previews_dir.mkdir(parents=True, exist_ok=True)
    slides = page.locator("[data-pptx-slide], .slide")
    count = slides.count()
    paths: list[Path] = []
    for i in range(count):
        out_png = previews_dir / f"slide-{i + 1:02d}.png"
        slides.nth(i).screenshot(path=str(out_png))
        paths.append(out_png)
    print(f"[export-previews] {count} PNGs salvos em {previews_dir}")
    return paths


def export_pptx(html_path: Path, out_pptx: Path, width_px: int, height_px: int) -> None:
    """Exporta PPTX 100% editável e fiel ao HTML via DOM measurement."""
    import shutil
    from measure import open_deck_page, measure
    from assemble import assemble, refresh_font_plan_caches
    from pptx_fixer import fix_pptx_file

    refresh_font_plan_caches()
    with tempfile.TemporaryDirectory(prefix="carousel_h2p_") as tmp:
        tmp_dir = Path(tmp)
        meas_path = tmp_dir / "measurement.json"
        raw_pptx = tmp_dir / "raw.pptx"

        with open_deck_page(html_path, viewport={"width": width_px, "height": height_px}) as page:
            measurement = measure(
                html_path,
                meas_path,
                no_screenshots=True,
                verbose=False,
                page=page,
            )

        slides = measurement.get("slides", [measurement])
        for s in slides:
            if "slide" in s:
                s["slide"]["width"] = width_px
                s["slide"]["height"] = height_px

        meas_path.write_text(json.dumps(measurement, ensure_ascii=False), encoding="utf-8")
        assemble(measurement, raw_pptx, width_px=width_px, height_px=height_px)
        out_pptx.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(raw_pptx, out_pptx)
        fix_pptx_file(out_pptx)
        print(f"[export-pptx] Salvo: {out_pptx} ({out_pptx.stat().st_size:,} B)")


def run_export(
    html_path: Path,
    *,
    out_pdf: Path | None = None,
    out_pptx: Path | None = None,
    previews_dir: Path | None = None,
    fmt: str | None = None,
    do_pdf: bool = True,
    do_pptx: bool = True,
) -> dict:
    t0 = time.perf_counter()
    html_path = html_path.resolve()
    if not html_path.exists():
        raise FileNotFoundError(f"HTML não encontrado: {html_path}")

    slug = html_path.parent.name if html_path.name == "index.html" else html_path.stem
    out_dir = html_path.parent
    pdf_path = out_pdf or (out_dir / f"{slug}.pdf")
    pptx_path = out_pptx or (out_dir / f"{slug}.pptx")

    from measure import open_deck_page

    if fmt and fmt in FORMAT_PRESETS:
        width_px, height_px = FORMAT_PRESETS[fmt]
    else:
        with open_deck_page(html_path, viewport={"width": 1080, "height": 1350}) as p:
            width_px, height_px = detect_stage_dimensions(p)

    print(f"[export-all] {html_path.name} ({width_px}x{height_px})")

    if do_pdf or previews_dir:
        with open_deck_page(html_path, viewport={"width": width_px, "height": height_px}) as page:
            if do_pdf:
                export_pdf(page, pdf_path, width_px, height_px)
            if previews_dir:
                export_previews(page, previews_dir, width_px, height_px)

    if do_pptx:
        export_pptx(html_path, pptx_path, width_px, height_px)

    elapsed = time.perf_counter() - t0
    print(f"[export-all] Concluído em {elapsed:.2f}s")
    return {
        "width": width_px,
        "height": height_px,
        "pdf": str(pdf_path) if do_pdf else None,
        "pptx": str(pptx_path) if do_pptx else None,
        "elapsed": round(elapsed, 2),
    }


def main():
    parser = argparse.ArgumentParser(description="Exporta HTML de Carrossel para PDF e PPTX editável.")
    parser.add_argument("html", help="Caminho para o index.html do carrossel")
    parser.add_argument("--format", choices=list(FORMAT_PRESETS.keys()), help="Forçar formato (4:5, 1:1, 16:9)")
    parser.add_argument("--pdf-only", action="store_true", help="Exportar apenas PDF")
    parser.add_argument("--pptx-only", action="store_true", help="Exportar apenas PPTX")
    parser.add_argument("--previews", action="store_true", help="Gerar PNGs em previews/")
    args = parser.parse_args()

    html_path = Path(args.html)
    previews_dir = (html_path.parent / "previews") if args.previews else None
    run_export(
        html_path,
        previews_dir=previews_dir,
        fmt=args.format,
        do_pdf=not args.pptx_only,
        do_pptx=not args.pdf_only,
    )


if __name__ == "__main__":
    main()
