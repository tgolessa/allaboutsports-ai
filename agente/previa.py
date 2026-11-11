"""Gera uma folha de prévia (JPEG) com os slides de um ou mais posts.

Uso: python agente/previa.py posts/2026-11-12-manha-01 posts/2026-11-12-manha-02 --out posts/_previas/2026-11-12-manha.jpg
"""
import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw

W, H, GAP = 270, 338, 16


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("posts", nargs="+")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    rows = []
    for p in a.posts:
        meta = json.loads((Path(p) / "post.json").read_text(encoding="utf-8"))
        rows.append([Image.open(Path(p) / rel).convert("RGB").resize((W, H)) for rel in meta["imagens"]])
    cols = max(len(r) for r in rows)
    sheet = Image.new("RGB", (GAP + cols * (W + GAP), GAP + len(rows) * (H + GAP + 28)), (232, 232, 236))
    draw = ImageDraw.Draw(sheet)
    y = GAP
    for p, r in zip(a.posts, rows):
        draw.text((GAP, y), Path(p).name, fill=(40, 40, 48))
        y += 22
        for k, im in enumerate(r):
            sheet.paste(im, (GAP + k * (W + GAP), y))
        y += H + GAP + 6
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    sheet.save(a.out, quality=85)
    print(a.out)


if __name__ == "__main__":
    main()
