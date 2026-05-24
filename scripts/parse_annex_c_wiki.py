"""One-off: parse Wikipedia Annex C dump -> data/external/annex_c_wc2026.json."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# Pass path to wiki text file as argv[1] or use default under repo
REPO = Path(__file__).resolve().parent.parent


def main() -> None:
    wiki_path = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO / "docs" / "annex_c_wiki_source.txt"
    if not wiki_path.exists():
        print(f"Missing {wiki_path}", file=sys.stderr)
        sys.exit(1)
    pat = re.compile(
        r"^\|\s*(\d+)\s*\|\s*([A-L])\s*\|\s*([A-L])\s*\|\s*([A-L])\s*\|\s*([A-L])\s*\|"
        r"\s*([A-L])\s*\|\s*([A-L])\s*\|\s*([A-L])\s*\|\s*([A-L])\s*\|"
        r"\s*(3[A-L])\s*\|\s*(3[A-L])\s*\|\s*(3[A-L])\s*\|\s*(3[A-L])\s*\|"
        r"\s*(3[A-L])\s*\|\s*(3[A-L])\s*\|\s*(3[A-L])\s*\|\s*(3[A-L])\s*\|"
    )
    rows: list[dict[str, object]] = []
    for line in wiki_path.read_text(encoding="utf-8").splitlines():
        m = pat.match(line)
        if not m:
            continue
        g = m.groups()
        adv = "".join(sorted(g[1:9]))
        thirds = tuple(x.replace("3", "") for x in g[9:])
        rows.append({"advancing_third_groups": adv, "slots_ABDE_GIKL": thirds})
    out = REPO / "data" / "external" / "annex_c_wc2026.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rows, indent=0), encoding="utf-8")
    print(f"wrote {out} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
