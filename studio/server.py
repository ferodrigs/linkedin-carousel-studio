#!/usr/bin/env python3
"""
server.py — Servidor local do LinkedIn Carousel Studio.

Inicia em http://127.0.0.1:4100 sem dependências externas de servidor.
Permite visualizar, ajustar tamanhos de fonte/espaçamentos/textos em tempo real,
salvar o HTML atualizado e exportar PDF + PPTX 100% fiéis ao HTML.
"""

from __future__ import annotations

import json
import mimetypes
import subprocess
import sys
import urllib.parse
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
STUDIO_DIR = ROOT_DIR / "studio"
CAROUSELS_DIR = ROOT_DIR / "carousels"
DESIGN_DIR = ROOT_DIR / "design-system"
ENGINE_SCRIPT = ROOT_DIR / "engine" / "export_all.py"

HOST = "127.0.0.1"
PORT = 4100


class StudioHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None:
        pass  # Keep console clean

    def _send_json(self, payload: dict | list, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, file_path: Path) -> None:
        if not file_path.exists() or not file_path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")
            return
        mime, _ = mimetypes.guess_type(str(file_path))
        content = file_path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", f"{mime or 'application/octet-stream'}; charset=utf-8" if (mime or "").startswith("text/") else (mime or "application/octet-stream"))
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(content)

    def _read_json_body(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length > 0 else b"{}"
        return json.loads(raw.decode("utf-8"))

    def do_GET(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/" or path == "/index.html":
            self._send_file(STUDIO_DIR / "index.html")
            return

        if path == "/api/carousels":
            items = []
            if CAROUSELS_DIR.exists():
                for d in sorted(CAROUSELS_DIR.iterdir()):
                    if d.is_dir() and (d / "index.html").exists():
                        slug = d.name
                        items.append({
                            "slug": slug,
                            "has_pdf": (d / f"{slug}.pdf").exists(),
                            "has_pptx": (d / f"{slug}.pptx").exists(),
                        })
            self._send_json({"carousels": items})
            return

        if path.startswith("/api/carousel/"):
            slug = urllib.parse.unquote(path.removeprefix("/api/carousel/")).strip("/")
            html_file = CAROUSELS_DIR / slug / "index.html"
            if not html_file.exists():
                self._send_json({"error": "Carrossel não encontrado"}, status=404)
                return
            self._send_json({
                "slug": slug,
                "html": html_file.read_text(encoding="utf-8"),
            })
            return

        # Static serving for carousels/ and design-system/
        if path.startswith("/carousels/"):
            rel = urllib.parse.unquote(path.removeprefix("/carousels/"))
            target = (CAROUSELS_DIR / rel).resolve()
            if str(target).startswith(str(CAROUSELS_DIR.resolve())):
                self._send_file(target)
                return

        if path.startswith("/design-system/"):
            rel = urllib.parse.unquote(path.removeprefix("/design-system/"))
            target = (DESIGN_DIR / rel).resolve()
            if str(target).startswith(str(DESIGN_DIR.resolve())):
                self._send_file(target)
                return

        self.send_error(HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/api/save":
            data = self._read_json_body()
            slug = data.get("slug", "").strip()
            html = data.get("html", "")
            if not slug or not html:
                self._send_json({"error": "slug e html são obrigatórios"}, status=400)
                return
            target = (CAROUSELS_DIR / slug / "index.html").resolve()
            if not str(target).startswith(str(CAROUSELS_DIR.resolve())):
                self._send_json({"error": "Caminho inválido"}, status=403)
                return
            target.write_text(html, encoding="utf-8")
            self._send_json({"ok": True, "saved": str(target)})
            return

        if path == "/api/export":
            data = self._read_json_body()
            slug = data.get("slug", "").strip()
            mode = data.get("mode", "all")  # "pdf", "pptx", "all"
            html_file = (CAROUSELS_DIR / slug / "index.html").resolve()
            if not html_file.exists():
                self._send_json({"error": "Carrossel não encontrado"}, status=404)
                return

            cmd = [sys.executable, str(ENGINE_SCRIPT), str(html_file)]
            if mode == "pdf":
                cmd.append("--pdf-only")
            elif mode == "pptx":
                cmd.append("--pptx-only")

            proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
            if proc.returncode != 0:
                self._send_json({"ok": False, "error": proc.stderr or proc.stdout}, status=500)
                return

            self._send_json({
                "ok": True,
                "log": proc.stdout,
                "pdf_url": f"/carousels/{slug}/{slug}.pdf" if (CAROUSELS_DIR / slug / f"{slug}.pdf").exists() else None,
                "pptx_url": f"/carousels/{slug}/{slug}.pptx" if (CAROUSELS_DIR / slug / f"{slug}.pptx").exists() else None,
            })
            return

        self.send_error(HTTPStatus.NOT_FOUND)


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), StudioHandler)
    print(f"[LinkedIn Carousel Studio] Rodando em http://{HOST}:{PORT}")
    print("Pressione Ctrl+C para encerrar.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nEncerrando Studio...")
        server.server_close()


if __name__ == "__main__":
    main()
