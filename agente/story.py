"""
AllAboutSports.AI — gera o Story (9:16) que acompanha um post do feed.

Uso: python agente/story.py posts/<pasta>/pauta.json [--out posts/<pasta>]

Cria story.jpg: a capa do post redesenhada em 1080x1920, com o rodapé
trocado por "Post novo no perfil". O publicador publica o Story logo
depois do post, quando o arquivo existe.
"""
import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "templates"))
import render as r  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pauta")
    ap.add_argument("--out")
    a = ap.parse_args()
    pauta_path = Path(a.pauta).resolve()
    out_dir = Path(a.out).resolve() if a.out else pauta_path.parent
    d = json.loads(pauta_path.read_text(encoding="utf-8"))
    builders = {"noticia": r.build_noticia, "nota": r.build_nota,
                "semanal": r.build_semanal, "ranking": r.build_ranking}
    capa = builders[d["tipo"]](d)[0]
    for old in ("<strong>Arraste →</strong>", "<strong>Nota rápida</strong>", "<strong>01/07 →</strong>"):
        capa = capa.replace(old, "<strong>Post novo no perfil ↑</strong>")
    with tempfile.TemporaryDirectory() as tmp:
        r.render([capa], Path(tmp), "vertical")
        out_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy(Path(tmp) / "01.jpg", out_dir / "story.jpg")
    print(out_dir / "story.jpg")


if __name__ == "__main__":
    main()
