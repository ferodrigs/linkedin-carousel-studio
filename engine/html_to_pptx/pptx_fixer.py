"""pptx_fixer.py — OpenXML Post-Processor to sanitize .pptx archives.

Ported from abdelkrimkr/html2pptx (lib/pptx-fixer.js) into Python:
1. Empty name attributes in <p:cNvPr id="X" name=""/> -> name="Shape X"
2. Empty <a:ln></a:ln> or <a:ln/> elements with no attributes -> removed
3. Zero dimensions in <a:ext cx="0" cy="0"/> -> minimum 1 EMU
4. Conflicting autofit settings (<a:normAutofit/> + <a:spAutoFit/>) -> keep normAutofit
5. Very small cy="XXXX" (< 10000 EMUs) -> cy="10000"
6. Negative charset attributes (e.g. charset="-122") -> charset="0"
"""
import re
import shutil
import zipfile
from pathlib import Path


class PPTXFixer:
    def __init__(self):
        self.fix_count = 0

    def fix_xml(self, xml: str) -> str:
        fixed = xml

        # FIX 1: Empty name attributes in p:cNvPr
        def _fix_cnvpr_self(m):
            self.fix_count += 1
            sid = m.group(1)
            return f'<p:cNvPr id="{sid}" name="Shape {sid}"/>'

        fixed = re.sub(r'<p:cNvPr\s+id="(\d+)"\s+name=""\s*/>', _fix_cnvpr_self, fixed)

        def _fix_cnvpr_open(m):
            self.fix_count += 1
            sid, inner = m.group(1), m.group(2)
            return f'<p:cNvPr id="{sid}" name="Shape {sid}">{inner}</p:cNvPr>'

        fixed = re.sub(r'<p:cNvPr\s+id="(\d+)"\s+name="">([^<]*)</p:cNvPr>', _fix_cnvpr_open, fixed)

        # FIX 2: Empty a:ln elements
        def _fix_empty_ln(m):
            self.fix_count += 1
            return ""

        fixed = re.sub(r'<a:ln\s*></a:ln>', _fix_empty_ln, fixed)
        fixed = re.sub(r'<a:ln\s*/>', _fix_empty_ln, fixed)

        # FIX 3: Zero dimensions in transforms
        def _fix_zero_both(m):
            self.fix_count += 1
            return '<a:ext cx="1" cy="1"/>'

        fixed = re.sub(r'<a:ext\s+cx="0"\s+cy="0"\s*/>', _fix_zero_both, fixed)

        def _fix_zero_cx(m):
            self.fix_count += 1
            return f'<a:ext cx="1" cy="{m.group(1)}"/>'

        fixed = re.sub(r'<a:ext\s+cx="0"\s+cy="(\d+)"\s*/>', _fix_zero_cx, fixed)

        def _fix_zero_cy(m):
            self.fix_count += 1
            return f'<a:ext cx="{m.group(1)}" cy="1"/>'

        fixed = re.sub(r'<a:ext\s+cx="(\d+)"\s+cy="0"\s*/>', _fix_zero_cy, fixed)

        # FIX 4: Conflicting autofit settings (normAutofit + spAutoFit inside a:bodyPr)
        def _fix_autofit(m):
            self.fix_count += 1
            return f'{m.group(1)}{m.group(2)}<a:normAutofit/>{m.group(3)}'

        fixed = re.sub(
            r'(<a:bodyPr[^>]*>)((?:(?!</a:bodyPr>).)*?)<a:normAutofit\s*/>((?:(?!</a:bodyPr>).)*?)<a:spAutoFit\s*/>',
            _fix_autofit,
            fixed,
            flags=re.IGNORECASE | re.DOTALL,
        )

        # FIX 5: Very small cy dimensions (< 10000 EMUs) inside a:ext
        def _fix_small_cy(m):
            val = int(m.group(2))
            if 0 < val < 10000:
                self.fix_count += 1
                return f'<a:ext cx="{m.group(1)}" cy="10000"/>'
            return m.group(0)

        fixed = re.sub(r'<a:ext\s+cx="(\d+)"\s+cy="(\d{1,4})"\s*/>', _fix_small_cy, fixed)

        # FIX 6: Negative charset attributes
        def _fix_charset(m):
            val = int(m.group(1))
            if val < 0:
                self.fix_count += 1
                return 'charset="0"'
            return m.group(0)

        fixed = re.sub(r'charset="(-?\d+)"', _fix_charset, fixed)

        return fixed

    def fix_pptx(self, pptx_path: Path) -> dict:
        pptx_path = Path(pptx_path).resolve()
        self.fix_count = 0
        with zipfile.ZipFile(pptx_path, "r") as zin:
            entries = {name: zin.read(name) for name in zin.namelist()}

        modified = False
        for name, raw in list(entries.items()):
            if name.endswith(".xml") or name.endswith(".rels"):
                text = raw.decode("utf-8", errors="replace")
                fixed = self.fix_xml(text)
                if fixed != text:
                    entries[name] = fixed.encode("utf-8")
                    modified = True

        if modified:
            tmp_path = pptx_path.with_suffix(".pptx.tmp")
            with zipfile.ZipFile(tmp_path, "w", zipfile.ZIP_DEFLATED) as zout:
                for name, data in entries.items():
                    zout.writestr(name, data)
            shutil.move(str(tmp_path), str(pptx_path))

        return {"success": True, "fix_count": self.fix_count}


def fix_pptx_file(pptx_path: Path) -> dict:
    return PPTXFixer().fix_pptx(pptx_path)
