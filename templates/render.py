"""
AllAboutSports.AI — renderizador de carrosséis.

Uso:
    python render.py data/exemplo-noticia.json
    python render.py data/exemplo-resumo.json --out out/resumo

Lê um JSON de pauta, monta os slides em HTML com a identidade visual
(base.css) e salva um PNG 1080x1350 por slide.

Tipos de JSON:
  "noticia" -> carrossel A (7 slides, identidade cobalto)
  "nota"    -> nota rápida A (1 ou 2 slides)
  "semanal" -> top 10 da semana C (7 slides, identidade terminal)
  "ranking" -> ranking da quinzena C (7 slides, contagem regressiva)
"""
import argparse
import html
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
CHROME = "/usr/bin/google-chrome"
TOTAL = 7


def e(text):
    return html.escape(str(text or ""))


def counter(i, total=None):
    return f"{i:02d}/{(total or TOTAL):02d}"


# Ajuste automático: diminui a fonte de elementos que estouram a largura
# (.fit-w) e, se o slide inteiro estourar a altura, diminui os textos .fit-h.
FIT_JS = """
() => {
  for (const el of document.querySelectorAll('.fit-w')) {
    let fs = parseFloat(getComputedStyle(el).fontSize);
    const max = el.parentElement.clientWidth;
    while (el.scrollWidth > max && fs > 40) { fs *= 0.96; el.style.fontSize = fs + 'px'; }
  }
  const slide = document.querySelector('.slide');
  const blocks = [...document.querySelectorAll('.fit-h')];
  let guard = 0;
  while (slide.scrollHeight > slide.clientHeight + 1 && blocks.length && guard < 60) {
    for (const el of blocks) {
      const fs = parseFloat(getComputedStyle(el).fontSize) * 0.96;
      el.style.fontSize = fs + 'px';
    }
    guard++;
  }
  return { overflow: slide.scrollHeight > slide.clientHeight + 1, shrinkSteps: guard };
}
"""


def page(inner, cls):
    return f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<link rel="stylesheet" href="base.css"></head>
<body><div class="slide {cls}">{inner}</div></body></html>"""


def tri(direction, size=34):
    if direction == "down":
        path = "M0 0 L120 0 L60 104 Z"
    elif direction == "up":
        path = "M60 0 L120 104 L0 104 Z"
    else:
        return f'<svg width="{size}" height="{size}" viewBox="0 0 120 120"><rect x="0" y="45" width="120" height="30" fill="currentColor"/></svg>'
    return f'<svg width="{size}" height="{int(size*104/120)}" viewBox="0 0 120 104"><path d="{path}" fill="currentColor"/></svg>'


# ---------------------------------------------------------------- A
def a_top(i, cobalt=False, total=None):
    return f'<div class="top"><span class="brand">AllAboutSports<b>.AI</b></span><span class="counter">{counter(i, total)}</span></div>'


def a_foot(left, right="→"):
    return f'<div class="foot"><span>{e(left)}</span><strong>{e(right)}</strong></div>'


def a_text_slide(i, label, text, source, cobalt=False):
    inner = (
        a_top(i, cobalt)
        + f'<div class="body"><div class="label"><i></i><span>{e(label)}</span></div>'
        + f'<p class="text fit-h">{e(text)}</p></div>'
        + a_foot(f"Fonte: {source}")
    )
    return page(inner, "a cobalt" if cobalt else "a")


def build_noticia(d):
    src = d["fonte"]
    capa = d["capa"]
    slides = []

    slides.append(page(
        f'<div class="top"><span class="brand">AllAboutSports<b>.AI</b></span><span class="pillar">{e(d["pilar"])}</span></div>'
        f'<div class="cover-hero">'
        + (f'<span class="cover-prefix">{e(capa.get("prefixo"))}</span>' if capa.get("prefixo") else "")
        + f'<span class="cover-number fit-w">{e(capa["numero"])}</span>'
        f'<span class="cover-title fit-h">{e(capa["manchete"])}</span></div>'
        + a_foot(f"Fonte: {src}", "Arraste →"),
        "a",
    ))

    slides.append(a_text_slide(2, "O fato", d["fato"], src))

    n = d["numero"]
    comp = n.get("comparacao") or []
    bars = ""
    if comp:
        top = max(c["valor"] for c in comp) or 1
        for k, c in enumerate(comp):
            hl = " hl" if k == len(comp) - 1 else ""
            width = round(920 * c["valor"] / top)
            bars += f'<div class="bar-row{hl}"><span>{e(c["rotulo"])}</span><i style="width:{width}px"></i></div>'
    slides.append(page(
        a_top(3)
        + f'<div class="body"><div class="label"><i></i><span>O número</span></div>'
        f'<div style="display:flex;flex-direction:column;gap:8px"><span class="big fit-w">{e(n["valor"])}</span>'
        f'<span class="big-caption fit-h">{e(n["legenda"])}</span></div>'
        + (f'<div class="bars">{bars}</div>' if bars else "")
        + "</div>"
        + a_foot(f"Fonte: {src}"),
        "a",
    ))

    slides.append(a_text_slide(4, "Contexto", d["contexto"], src))
    slides.append(a_text_slide(5, "Por que importa", d["por_que_importa"], src, cobalt=True))
    slides.append(a_text_slide(6, "O que observar", d["o_que_observar"], src))

    fontes = "<br>".join(e(f) for f in d.get("fontes", [src]))
    slides.append(page(
        a_top(7)
        + '<div class="body" style="gap:72px"><span class="closing">O negócio do esporte, todo dia<b>.</b></span>'
        '<div class="actions"><span class="btn">Siga @allaboutsports.ai</span><span class="btn ghost">Salve este post</span></div>'
        f'<div class="sources"><h4>Fontes</h4><p>{fontes}</p></div></div>'
        + a_foot("Conteúdo produzido por IA com revisão humana", "Fim"),
        "a",
    ))
    return slides


# ------------------------------------------------------- A · nota rápida
def build_nota(d):
    """Nota rápida: 1 slide (manchete + número + contexto) e, se houver
    'por_que_importa', um 2º slide em cobalto."""
    src = d["fonte"]
    total = 2 if d.get("por_que_importa") else 1
    prefix = f'<span class="cover-prefix">{e(d.get("prefixo"))}</span>' if d.get("prefixo") else ""
    right = "Arraste →" if total == 2 else "Nota rápida"
    slides = [page(
        f'<div class="top"><span class="brand">AllAboutSports<b>.AI</b></span><span class="pillar">{e(d["pilar"])}</span></div>'
        f'<div class="cover-hero" style="gap:32px">{prefix}'
        f'<span class="cover-number fit-w" style="font-size:320px">{e(d["numero"])}</span>'
        f'<span class="cover-title fit-h">{e(d["manchete"])}</span>'
        f'<p class="note-text fit-h">{e(d["contexto"])}</p></div>'
        + a_foot(f"Fonte: {src}", right),
        "a",
    )]
    if total == 2:
        slides.append(page(
            a_top(2, total=2)
            + f'<div class="body"><div class="label"><i></i><span>Por que importa</span></div>'
            f'<p class="text fit-h">{e(d["por_que_importa"])}</p></div>'
            + a_foot("Siga @allaboutsports.ai", "Fim"),
            "a cobalt",
        ))
    return slides


# ---------------------------------------------------------------- C
def c_top(tag):
    return f'<div class="top"><span class="brand">ALLABOUTSPORTS<b>.AI</b></span><span class="tag">{e(tag)}</span></div>'


def c_foot(left, right):
    return f'<div class="foot"><span>{e(left)}</span><strong>{e(right)}</strong></div>'


def c_block(label, signal_html, number, title, text):
    """Meio slide do visual C: rótulo, sinal, número, título e uma linha de contexto."""
    return (
        '<div class="block">'
        f'<div class="block-head"><span class="rank">{e(label)}</span>{signal_html}</div>'
        f'<span class="ticker-sm fit-w">{e(number)}</span>'
        f'<span class="block-title fit-h">{e(title)}</span>'
        f'<p class="block-text fit-h">{e(text)}</p>'
        '</div>'
    )


def c_signal(item):
    d = item.get("direcao", "flat")
    return f'<span class="signal {d}">{tri(d, 26)}<span>{e(item.get("sinal", ""))}</span></span>'


def c_closing(tag, sources, line):
    fontes = " · ".join(e(f) for f in dict.fromkeys(sources))
    return page(
        c_top(tag)
        + '<div class="stack" style="gap:56px"><span class="headline">Até segunda<b>_</b></span>'
        f'<p class="c-text">{e(line)}</p>'
        '<div class="cta"><span class="solid">SIGA @ALLABOUTSPORTS.AI</span><span>SALVE</span></div></div>'
        + c_foot(f"FONTES: {fontes.upper()}", "FIM"),
        "c",
    )


def build_semanal(d):
    """Top 10 da semana: capa com a lista, 5 slides com 2 notícias, fechamento."""
    news = d["noticias"]
    if len(news) != 10:
        sys.exit("O resumo semanal precisa de exatamente 10 notícias.")
    tag = f'SEMANA {d["semana"]}'
    rows = "".join(
        f'<div class="row compact"><span class="n">{k+1:02d}</span><span class="t">{e(x["titulo_curto"])}</span>'
        f'<span class="v {x.get("direcao", "flat")}">{tri(x.get("direcao", "flat"), 20)} {e(x["numero"])}</span></div>'
        for k, x in enumerate(news)
    )
    slides = [page(
        c_top(tag)
        + f'<div class="stack" style="gap:20px"><span class="period">{e(d["periodo"])}</span>'
        '<span class="headline" style="font-size:112px">Top 10<br>da semana<b>_</b></span></div>'
        f'<div class="list">{rows}</div>'
        + c_foot("10 NOTÍCIAS · 2 MINUTOS", f"{counter(1)} →"),
        "c",
    )]
    for s in range(5):
        pair = news[2 * s: 2 * s + 2]
        blocks = "".join(
            c_block(f"{2*s+k+1:02d} · {x['pilar'].upper()}", c_signal(x), x["numero"], x["titulo"], x["resumo"])
            for k, x in enumerate(pair)
        )
        src = " · ".join(dict.fromkeys(x["fonte"] for x in pair))
        slides.append(page(
            c_top(tag) + f'<div class="pair">{blocks}</div>'
            + c_foot(f"FONTES: {src.upper()}", f"{counter(s + 2)} →"),
            "c",
        ))
    slides.append(c_closing(tag, [x["fonte"] for x in news],
                            "Toda sexta, as 10 notícias que mexeram com o dinheiro do esporte."))
    return slides


def build_ranking(d):
    """Ranking da quinzena: os 10 maiores valores, em contagem regressiva do 10º ao 1º.
    'itens' vem em ordem do 1º (maior) ao 10º."""
    items = d["itens"]
    if len(items) != 10:
        sys.exit("O ranking precisa de exatamente 10 itens.")
    tag = f'QUINZENA {d["quinzena"]}'
    slides = [page(
        c_top(tag)
        + f'<div class="stack" style="gap:28px"><span class="period">{e(d["periodo"])}</span>'
        '<span class="headline">Ranking<br>da quinzena<b>_</b></span>'
        f'<p class="c-text">{e(d.get("subtitulo", "Os 10 maiores valores do esporte nas últimas duas semanas."))}</p></div>'
        '<div class="countdown"><span>10</span><span>09</span><span>08</span><span>07</span><span>06</span>'
        '<span>05</span><span>04</span><span>03</span><span>02</span><span class="first">01</span></div>'
        + c_foot("DO 10º AO 1º", f"{counter(1)} →"),
        "c",
    )]
    order = list(range(9, -1, -1))  # índices do 10º ao 1º
    for s in range(5):
        idx = order[2 * s: 2 * s + 2]
        blocks = "".join(
            c_block(f"#{i+1:02d} · {items[i]['categoria'].upper()}", "", items[i]["numero"], items[i]["titulo"], items[i]["resumo"])
            for i in idx
        )
        src = " · ".join(dict.fromkeys(items[i]["fonte"] for i in idx))
        cls = "c podium" if s == 4 else "c"
        slides.append(page(
            c_top(tag) + f'<div class="pair">{blocks}</div>'
            + c_foot(f"FONTES: {src.upper()}", f"{counter(s + 2)} →"),
            cls,
        ))
    slides.append(c_closing(tag, [x["fonte"] for x in items],
                            "A cada quinze dias, o ranking dos maiores valores do esporte."))
    return slides


# ---------------------------------------------------------------- main
def render(slides, out_dir):
    out_dir.mkdir(parents=True, exist_ok=True)
    reports = []
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROME, args=["--no-sandbox"])
        ctx = browser.new_context(viewport={"width": 1080, "height": 1350}, device_scale_factor=1)
        pg = ctx.new_page()
        for i, doc in enumerate(slides, 1):
            tmp = ROOT / f".slide_{i:02d}.html"
            tmp.write_text(doc, encoding="utf-8")
            pg.goto(tmp.as_uri())
            pg.evaluate("document.fonts.ready")
            pg.wait_for_timeout(150)
            rep = pg.evaluate(FIT_JS)
            target = out_dir / f"{i:02d}.jpg"
            # A Meta aceita apenas JPEG na publicação via API.
            pg.screenshot(path=str(target), type="jpeg", quality=92,
                          clip={"x": 0, "y": 0, "width": 1080, "height": 1350})
            tmp.unlink()
            reports.append((target.name, rep))
        browser.close()
    return reports


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("data")
    ap.add_argument("--out")
    args = ap.parse_args()
    data_path = Path(args.data)
    d = json.loads(data_path.read_text(encoding="utf-8"))
    builders = {"noticia": build_noticia, "nota": build_nota, "semanal": build_semanal, "ranking": build_ranking}
    if d.get("tipo") not in builders:
        sys.exit('Campo "tipo" deve ser "noticia", "nota", "semanal" ou "ranking".')
    out_dir = Path(args.out) if args.out else ROOT / "out" / data_path.stem
    for name, rep in render(builders[d["tipo"]](d), out_dir):
        flag = "  ESTOUROU" if rep["overflow"] else ""
        print(f"{out_dir.name}/{name}  ajustes={rep['shrinkSteps']}{flag}")


if __name__ == "__main__":
    main()
