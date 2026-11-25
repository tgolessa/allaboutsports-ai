"""
AllAboutTri.AI — renderizador de posts (identidade "Split").

Uso:
    python render.py data/exemplo-noticia.json
    python render.py data/exemplo-resumo.json --out out/resumo

Lê um JSON de pauta, monta os slides em HTML com a identidade visual
(base.css) e salva um PNG 1080x1350 por slide.

Tipos de JSON (exemplos em templates/exemplos/):
  "noticia"   -> carrossel de notícia (7 slides)
  "nota"      -> post de uma imagem (1 ou 2 slides)
  "resultado" -> resultado de prova: capa + tabela por categoria + fechamento
  "inscricao" -> abertura de inscrições: capa + ficha + fechamento
  "semanal"   -> top 10 da semana (7 slides)
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
  const main = document.querySelector('.main');
  const blocks = [...document.querySelectorAll('.fit-h')];
  let guard = 0;
  const over = () => slide.scrollHeight > slide.clientHeight + 1 || (main && main.scrollHeight > main.clientHeight + 1);
  while (over() && blocks.length && guard < 60) {
    for (const el of blocks) {
      const fs = parseFloat(getComputedStyle(el).fontSize) * 0.96;
      el.style.fontSize = fs + 'px';
    }
    guard++;
  }
  return { overflow: over(), shrinkSteps: guard };
}
"""


def page(inner, cls=""):
    return f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<link rel="stylesheet" href="base.css"></head>
<body><div class="slide {cls}">{inner}</div></body></html>"""


HANDLE = "@allabouttri.ai"


def top(tag):
    return (f'<div class="top"><span>AllAboutTri<b>.AI</b></span><span class="tag">{e(tag)}</span></div>'
            '<div class="tribar"><i class="s"></i><i class="b"></i><i class="r"></i></div>')


def foot(left, right="→"):
    return f'<div class="foot"><span>{e(left)}</span><strong>{e(right)}</strong></div>'


def splits(dados):
    if not dados:
        return ""
    cells = "".join(f'<div><span>{e(x["rotulo"])}</span><strong>{e(x["valor"])}</strong></div>' for x in dados[:3])
    return f'<div class="splits">{cells}</div>'


def hero(numero, unidade=None, size=None):
    st = f' style="font-size:{size}px"' if size else ""
    un = f"<small>{e(unidade)}</small>" if unidade else ""
    return f'<span class="hero-num fit-w"{st}>{e(numero)}{un}</span>'


def text_slide(i, total, kicker, text, src, dark=False):
    return page(
        top(counter(i, total))
        + f'<div class="main top-aligned"><span class="kicker">{e(kicker)}</span><p class="text fit-h">{e(text)}</p></div>'
        + foot(f"Fonte: {src}"),
        "dark" if dark else "",
    )


def closing(i, total, fontes, line="Triathlon, todo dia"):
    fs = "<br>".join(e(f) for f in dict.fromkeys(fontes))
    src = f'<div class="sources"><h4>Fontes</h4><p class="fit-h">{fs}</p></div>' if fs else ""
    return page(
        top(counter(i, total))
        + f'<div class="main" style="gap:64px"><span class="closing">{e(line)}<b>.</b></span>'
        f'<div class="actions"><span class="btn">Siga {HANDLE}</span><span class="btn ghost">Mande pro seu grupo de treino</span></div>'
        f'{src}</div>'
        + foot("Conteúdo produzido por IA, com fonte em todo post", "Fim"),
    )


# ------------------------------------------------------------ notícia
def build_noticia(d):
    src, capa = d["fonte"], d["capa"]
    pre = f'<span class="prefix">{e(capa["prefixo"])}</span>' if capa.get("prefixo") else ""
    slides = [page(
        top(d["editoria"])
        + f'<div class="main">{pre}{hero(capa["numero"], capa.get("unidade"))}'
        f'<span class="headline fit-h">{e(capa["manchete"])}</span></div>'
        + (f'<div style="padding-bottom:36px">{splits(capa.get("dados"))}</div>' if capa.get("dados") else "")
        + foot(f"Fonte: {src}", "Arraste →"),
    )]
    slides.append(text_slide(2, 7, "O fato", d["fato"], src))
    n = d["numero"]
    bars = ""
    comp = n.get("comparacao") or []
    if comp:
        mx = max(c["valor"] for c in comp) or 1
        for k, c in enumerate(comp):
            hl = " hl" if k == len(comp) - 1 else ""
            bars += f'<div class="bar-row{hl}"><span>{e(c["rotulo"])}</span><i style="width:{round(936 * c["valor"] / mx)}px"></i></div>'
    slides.append(page(
        top(counter(3, 7))
        + '<div class="main top-aligned"><span class="kicker">O número</span>'
        f'<span class="big fit-w">{e(n["valor"])}</span><span class="big-caption fit-h">{e(n["legenda"])}</span>'
        + (f'<div class="bars">{bars}</div>' if bars else "") + "</div>"
        + foot(f"Fonte: {src}"),
    ))
    slides.append(text_slide(4, 7, "Contexto", d["contexto"], src))
    slides.append(text_slide(5, 7, "Por que importa", d["por_que_importa"], src, dark=True))
    slides.append(text_slide(6, 7, "O que observar", d["o_que_observar"], src))
    slides.append(closing(7, 7, d.get("fontes", [src])))
    return slides


# ------------------------------------------------------------ nota
def build_nota(d):
    src = d["fonte"]
    total = 2 if d.get("por_que_importa") else 1
    pre = f'<span class="prefix">{e(d["prefixo"])}</span>' if d.get("prefixo") else ""
    slides = [page(
        top(d["editoria"])
        + f'<div class="main" style="gap:30px">{pre}{hero(d["numero"], d.get("unidade"), 270)}'
        f'<span class="headline fit-h">{e(d["manchete"])}</span><p class="note fit-h">{e(d["contexto"])}</p></div>'
        + foot(f"Fonte: {src}", "Arraste →" if total == 2 else HANDLE),
    )]
    if total == 2:
        slides.append(page(
            top(counter(2, 2))
            + f'<div class="main top-aligned"><span class="kicker">Por que importa</span><p class="text fit-h">{e(d["por_que_importa"])}</p></div>'
            + foot(f"Siga {HANDLE}", "Fim"),
            "dark",
        ))
    return slides


# ------------------------------------------------------------ resultado
def build_resultado(d):
    """Resultado de prova. 'categorias': 1 ou 2 (ex.: Pro feminino, Pro masculino),
    cada uma com 'podio' de 3 a 10 atletas (pos, atleta, pais, tempo, parciais opcionais)."""
    cats = d["categorias"]
    total = 2 + len(cats)
    src = d["fonte"]
    win = []
    for c in cats:
        w = c["podio"][0]
        win.append(f'<div><span>{e(c["nome"])}</span><strong class="winner">{e(w["atleta"])}</strong></div>')
    first = cats[0]["podio"][0]
    slides = [page(
        top(d.get("editoria", "Resultado"))
        + f'<div class="main" style="gap:28px"><span class="prefix">{e(d["prova"])} · {e(d["data"])}</span>'
        f'{hero(first["tempo"], None, 250)}'
        f'<span class="headline fit-h">{e(d["manchete"])}</span></div>'
        + f'<div class="splits" style="grid-template-columns:repeat({len(win)},1fr);padding-bottom:36px">{"".join(win)}</div>'
        + foot(f"Fonte: {src}", "Arraste →"),
    )]
    for k, c in enumerate(cats, 2):
        pod = c["podio"][:10]
        compact = " compact" if len(pod) > 5 else ""
        rows = ""
        for p in pod:
            par = p.get("parciais")
            sub = e(p.get("pais", ""))
            if par:
                sub += f' · S {e(par.get("natacao", "-"))} · B {e(par.get("bike", "-"))} · R {e(par.get("corrida", "-"))}'
            rows += (f'<div class="res"><span class="pos">{e(p["pos"])}</span><div class="who"><strong>{e(p["atleta"])}</strong>'
                     f'<span>{sub}</span></div><span class="time">{e(p["tempo"])}</span></div>')
        obs = f'<p class="note fit-h" style="font-size:30px">{e(c["observacao"])}</p>' if c.get("observacao") else ""
        slides.append(page(
            top(counter(k, total))
            + f'<div class="main top-aligned" style="padding-top:60px;gap:30px"><span class="kicker">{e(c["nome"])}</span>'
            f'<div class="results{compact}">{rows}</div>{obs}</div>'
            + foot(f"Fonte: {src}"),
        ))
    slides.append(closing(total, total, d.get("fontes", [src])))
    return slides


# ------------------------------------------------------------ inscrição
def build_inscricao(d):
    """Abertura de inscrições: capa com a data de abertura, ficha da prova e fechamento."""
    src = d["fonte"]
    slides = [page(
        top(d.get("editoria", "Inscrições"))
        + f'<div class="main" style="gap:28px"><span class="prefix">{e(d.get("prefixo", "Inscrições abrem"))}</span>'
        f'{hero(d["abertura"], None, 250)}'
        f'<span class="headline fit-h">{e(d["manchete"])}</span></div>'
        + (f'<div style="padding-bottom:36px">{splits(d.get("dados"))}</div>' if d.get("dados") else "")
        + foot(f"Fonte: {src}", "Arraste →"),
    )]
    rows = "".join(f'<div class="row"><span>{e(x["rotulo"])}</span><strong>{e(x["valor"])}</strong></div>' for x in d["itens"])
    obs = f'<p class="note fit-h" style="font-size:32px">{e(d["observacao"])}</p>' if d.get("observacao") else ""
    slides.append(page(
        top(counter(2, 3))
        + f'<div class="main top-aligned" style="gap:34px"><span class="kicker">{e(d["prova"])}</span>'
        f'<div class="sheet">{rows}</div>{obs}</div>'
        + foot(f"Fonte: {src}"),
    ))
    slides.append(closing(3, 3, d.get("fontes", [src]), "Salve e marque quem vai com você"))
    return slides


# ------------------------------------------------------------ semanal
def build_semanal(d):
    news = d["noticias"]
    if len(news) != 10:
        sys.exit("O resumo semanal precisa de exatamente 10 notícias.")
    items = "".join(f'<div class="item"><span>{k+1:02d}</span><strong>{e(x["titulo_curto"])}</strong></div>' for k, x in enumerate(news))
    slides = [page(
        top(f'Semana {d["semana"]}')
        + f'<div class="main" style="gap:30px"><span class="prefix">{e(d["periodo"])}</span>'
        '<span class="closing" style="font-size:118px">Top 10 da semana<b>.</b></span>'
        f'<div class="list">{items}</div></div>'
        + foot("10 notícias · 2 minutos", "Arraste →"),
    )]
    for s in range(5):
        pair = news[2 * s: 2 * s + 2]
        blocks = ""
        for k, x in enumerate(pair):
            num = f'<span class="b-num fit-w">{e(x["numero"])}</span>' if x.get("numero") else ""
            blocks += (f'<div class="block"><span class="kicker">{2*s+k+1:02d} · {e(x["editoria"])}</span>{num}'
                       f'<span class="b-title fit-h">{e(x["titulo"])}</span><p class="b-text fit-h">{e(x["resumo"])}</p></div>')
        src = " · ".join(dict.fromkeys(x["fonte"] for x in pair))
        slides.append(page(top(counter(s + 2, 7)) + f'<div class="main" style="gap:0">{blocks}</div>' + foot(f"Fontes: {src}")))
    slides.append(closing(7, 7, [x["fonte"] for x in news], "Toda sexta, o resumo da semana"))
    return slides


BUILDERS = {"noticia": build_noticia, "nota": build_nota, "resultado": build_resultado,
            "inscricao": build_inscricao, "semanal": build_semanal}


# ---------------------------------------------------------------- main
SIZES = {"feed": (1080, 1350), "vertical": (1080, 1920)}


def render(slides, out_dir, formato="feed"):
    w, h = SIZES[formato]
    if formato == "vertical":
        # 9:16 para Reels: mesma arte, com margens de segurança para a
        # interface do Instagram (topo, legenda/botões embaixo e à direita).
        slides = [s.replace('<html lang="pt-BR">', '<html lang="pt-BR" class="v">') for s in slides]
    out_dir.mkdir(parents=True, exist_ok=True)
    reports = []
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROME, args=["--no-sandbox"])
        ctx = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=1)
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
                          clip={"x": 0, "y": 0, "width": w, "height": h})
            tmp.unlink()
            reports.append((target.name, rep))
        browser.close()
    return reports


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("data")
    ap.add_argument("--out")
    ap.add_argument("--vertical", action="store_true", help="gera em 1080x1920 (Reels)")
    args = ap.parse_args()
    data_path = Path(args.data)
    d = json.loads(data_path.read_text(encoding="utf-8"))
    builders = BUILDERS
    if d.get("tipo") not in builders:
        sys.exit('Campo "tipo" deve ser um destes: ' + ", ".join(BUILDERS))
    out_dir = Path(args.out) if args.out else ROOT / "out" / data_path.stem
    for name, rep in render(builders[d["tipo"]](d), out_dir, "vertical" if args.vertical else "feed"):
        flag = "  ESTOUROU" if rep["overflow"] else ""
        print(f"{out_dir.name}/{name}  ajustes={rep['shrinkSteps']}{flag}")


if __name__ == "__main__":
    main()
